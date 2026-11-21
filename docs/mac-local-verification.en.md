# Verifying Ansible and GitHub Actions locally on a Mac — findings

Last updated: 2026-11-21

## Summary and conclusions

To verify Ansible roles and GitHub Actions workflows on a Mac, **we use podman (applehv + Rosetta)**. On a Mac running macOS 27 we confirmed that x86_64 (amd64) Linux containers (Ubuntu 22.04 / 24.04 / 26.04) run under Rosetta.

- **Ansible**: besides lint and check mode, apply roles to amd64 containers with Molecule's Podman driver and check idempotence.
- **GitHub Actions**: day-to-day checks run on Local CI (formerly Agent CI; it runs the official runner locally), using a fork with our fixes. Differences from the real GitHub Actions are recorded by a weekly parity comparison; apart from known, documented differences there are none left. Things that only exist on GitHub (OIDC etc.) are checked on a test branch with an ephemeral self-hosted runner.
- **x86**: Rosetta on macOS 27 supports up to x86-64-v3. Only packages that contain kernel modules need QEMU or a real x86 machine in the cloud.
- **Caveat**: podman 6's default provider on macOS (libkrun) does not support Rosetta and falls back to QEMU. The setting in containers.conf is required.

## Background: putting verification at the centre

The starting point is Lauren Tan's (SpaceXSI, Grokbot team) talk "[All Code Is Slop (Except Mine)](https://www.youtube.com/watch?v=O_zcc6Xl12g)" (AI Engineer Code Summit, 2026-11-11). Its message: if agents are going to write a lot of code, invest in the environment and in verification so that the right behaviour becomes the default.

- Order of constraints: codebase (design) → static analysis (lint, types) → verification (runtime, format) → prose (AGENTS.md etc.). The same feedback is turned into deterministic checks such as lint rules.
- Reviews become about looking at the evidence of verification (logs, videos, diffs). In practice: about 11,000 PRs a month with a revert rate of about 0.5%.
- Her plugin [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT, works with Claude Code) provides a playbook per kind of task (steps and completion criteria) and verification skills.

This investigation applies the idea to Ansible and GitHub Actions: find an environment where proof can be obtained on a Mac alone. For Ansible in particular, pstack's principle "Make Operations Idempotent" (running twice converges to the same state) applies directly.

## Verifying GitHub Actions locally

The everyday loop uses Local CI (Agent CI); the final check of features that only exist on GitHub uses a self-hosted runner. The options fall into three groups by "is the runner real?" and "is the GitHub server side real?".

| Option | Runner | Server side | Push | Strengths and weaknesses |
| --- | --- | --- | --- | --- |
| [Local CI / Agent CI](https://github.com/redwoodjs/local-ci) (redwoodjs) | Official | Emulated locally | Not needed | Pauses on the failing step so you can fix it and rerun only that step. Built for agents. 0.x, early stage |
| Self-hosted runner (ephemeral) | Official | GitHub.com | Needed | Covers OIDC, environments and real secrets. Run it on Linux if you use Docker actions |
| [act](https://github.com/nektos/act) | Reimplementation | Emulated | Not needed | Most widely used. Differs for `workflow_run` and actions that call the GitHub API |
| [wrkflw](https://github.com/bahdotsh/wrkflw) | Reimplementation | Emulated | Not needed | Similar to act |
| [runner.server](https://github.com/ChristopherHX/runner.server) | Fork of the official runner | Emulated locally | Not needed | The forerunner of the Agent CI idea. Last updated 2024 |

Always run `actionlint` (syntax, expressions, shellcheck) and `zizmor` (security) first as static checks.

**Notes on Local CI**

- The default runner image (`ghcr.io/actions/actions-runner`) has no `python3`. Workflows that run Ansible need their own Dockerfile (`.github/local-ci.Dockerfile`).
- It needs a Docker API. With podman, create `/var/run/docker.sock` with `podman-mac-helper install` (verified; see "Local CI + podman").
- Containers on a Mac are ARM64 by default. GitHub's `ubuntu-latest` is x86_64, so steps that assume `amd64` can differ.

## Verifying Ansible locally

No single test catches everything, so run the layers from the fastest. The core is [Molecule](https://github.com/ansible/molecule) (v26.6.0; create a throwaway instance → apply → verify → destroy).

| Layer | Tool | What it shows |
| --- | --- | --- |
| Static | `yamllint`, `ansible-lint`, `ansible-playbook --syntax-check` | Mistakes and discouraged patterns |
| Diff | `--check --diff` | Predicted changes. `command` / `shell` cannot be predicted |
| Apply | Molecule (Podman driver) | The result of actually applying to an amd64 container |
| Idempotence | Molecule's idempotence step | Whether the second run reports `changed=0` |
| Closer to production | tart Linux VMs, cloud VMs | Things containers do not reproduce: systemd, sysctl, reboots |

**Candidates for deterministic checks** (applying the talk's idea)

- Forbid `ignore_errors: yes` and `failed_when: false`, which silence failures, with a custom ansible-lint rule.
- Detect tasks whose URLs contain `amd64` / `x86_64` without branching on the architecture fact.
- Treat `continue-on-error: true` the same way on the GitHub Actions side.

Of pstack's playbooks, Investigation / Bug fix / Refactoring / Feature / Opening a PR / Babysit can be used as is. Autopilot-full / Shipping, which run all the way to merge automatically, should not be used on infrastructure where a merge goes straight to production. "Playbook" also clashes with Ansible terminology, so say "the Ansible playbook `site.yml`" explicitly when asking for work.

## Running x86 Linux on a Mac

Packages that only need user space can be handled **with Rosetta at close to native speed**. Use QEMU or a real x86 machine only when the kernel side has to be x86.

| Method | How | Speed | What does not work |
| --- | --- | --- | --- |
| Rosetta | Translates x86_64 user space on top of an ARM64 kernel | Close to native | Kernel modules, DKMS, drivers, 32-bit x86, AVX-512 (x86-64-v4) |
| QEMU full emulation | Emulates the x86 kernel and instructions | About 1/3 of native. The ratio is about the same on M6 | Almost nothing (just slow) |
| Real x86 | Cloud VMs, GitHub-hosted runners | Fast | Nothing (not on the Mac) |

**Tools that can use Rosetta**: podman (applehv only), Apple `container` (on by default), Colima / Lima (`--vz-rosetta`), OrbStack (`orb create --arch amd64`, paid for commercial use), tart (`tart run --rosetta=<tag>`, runs x86 binaries inside an ARM Linux VM).

**Tools that use QEMU**: Lima (`arch: "x86_64"`), Colima (`--arch x86_64`), UTM.

**Changes in macOS 27**: x86 translation for Linux is now part of the OS (`/Library/Apple/usr/libexec/oah/RosettaLinux`). Rosetta for Mac apps is being reduced in macOS 28, but Apple says x86 execution inside Linux VMs continues. On this Mac (macOS 27) we confirmed it can be used up to x86-64-v3 (next section).

**tart** is a macOS / Linux VM tool for Apple Silicon (now `openai/tart`, FSL-1.1-ALv2). Linux VMs are ARM only. The limit of two concurrent macOS VMs comes from Apple's licence, not from tart.

## Verification results (this Mac, macOS 27)

**Rosetta on macOS 27 supports x86-64-v3, and amd64 Ubuntu runs.** podman's default libkrun ends up on QEMU; after switching to applehv it ran on Rosetta. Done on 2026-11-18.

| Configuration | Translator (how checked) | Result |
| --- | --- | --- |
| podman 6.2.0, libkrun (default) | Only `qemu-x86_64` in binfmt. `"Rosetta": false` | QEMU. Cannot be used to judge Rosetta in this state |
| Same, after installing Rosetta again and recreating | No change | libkrun never supports Rosetta (confirmed in the source) |
| Apple `container` 1.7.1 (`--arch amd64`) | `/run/rosetta/rosetta` in `/proc/self/maps` | `x86-64-v3 (supported, searched)` on Ubuntu 22.04 / 24.04 / 26.04 |
| podman 6.2.0, applehv + `rosetta = true` | `rosetta` in binfmt, `/var/mnt/rosetta` in maps | `x86-64-v3 (supported, searched)` on Ubuntu 22.04 / 24.04 / 26.04 |

The command used to check (look at maps to see whether Rosetta or QEMU does the x86 translation; do not judge by speed alone):

```
podman run --rm --platform linux/amd64 docker.io/library/ubuntu:24.04 \
  sh -c 'grep -i -E "rosetta|qemu" /proc/self/maps | head -2; /lib64/ld-linux-x86-64.so.2 --help | grep -i "x86-64-v"'
```

Notes:

- QEMU also supports x86-64-v3, so under QEMU it "works" even where Rosetta is not supported. Always check which translator is used.
- A fresh macOS 27 only had `RosettaLinux` in `oah/`. `softwareupdate --install-rosetta` added `libRosettaRuntime` and others. Whether applehv requires them is still open.
- Apple `container` 1.7.1 has no option to disable Rosetta (`--rosetta` only enables it), so we could not compare its speed with QEMU. For reference: 3 million shell loop iterations took about 8 seconds (including start-up).

### Ubuntu (amd64)

**amd64 images of Ubuntu 22.04 / 24.04 / 26.04 also run on podman (applehv + Rosetta).** All have `/var/mnt/rosetta` in maps and support up to x86-64-v3. Ubuntu's baseline only requires the base x86-64 level.

| Image | Version | glibc | Translator | x86-64 levels |
| --- | --- | --- | --- | --- |
| `ubuntu:26.04` | Ubuntu 26.04.1 LTS | 2.43 | Rosetta | v2 and v3 supported, v4 not |
| `ubuntu:24.04` | Ubuntu 24.04.5 LTS | 2.39 | Rosetta | v2 and v3 supported, v4 not |
| `ubuntu:22.04` | Ubuntu 22.04.5 LTS | 2.35 | Rosetta | v2 and v3 supported, v4 not |

`uname -m` is `x86_64` and `dpkg --print-architecture` is `amd64` in all of them. `apt-get install curl python3` succeeded on `ubuntu:24.04` (exit 0, curl 8.5.0 x86_64-pc-linux-gnu, Python 3.12.3, about 18 seconds). Usable as Ansible targets.

### Speed of Rosetta and QEMU

**Rosetta takes 1.1–3.9× native time, QEMU 3–17×.** For branch-heavy work such as shell scripts, Rosetta is about 9× faster than QEMU. Measured on an Apple M4, macOS 27.2.1, podman 6.2.0 (applehv), `ubuntu:24.04`, 2026-11-18.

| Workload | arm64 native | amd64 + Rosetta | amd64 + QEMU |
| --- | --- | --- | --- |
| 3 million bash loop iterations | 3.86 s | 7.63 s (2.0×) | 67.49 s (17.5×) |
| gzip -1, 300 MB | 0.77 s | 0.83 s (1.1×) | 2.43 s (3.2×) |
| sha256sum, 300 MB | 0.16 s | 0.62 s (3.9×) | 1.66 s (10.6×) |

Ratios are relative to arm64 native. QEMU was run explicitly by passing the machine's `qemu-x86_64-static` (user mode) into the container. Full emulation of the kernel is expected to be slower still (not measured). Creating a libkrun machine for comparison with podman 6 was abandoned because `podman machine init` never returned.

### Molecule (Podman driver) + amd64 + systemd

**`molecule test` succeeded end to end.** In an amd64 Ubuntu 24.04 container, systemd ran as PID 1 under Rosetta, and a role that installs a package, places a config file and starts a service applied cleanly. Ansible core 2.22.0, Molecule 26.11.0, molecule-plugins 26.11.0, Python 3.13, 2026-11-18.

| Stage | Result |
| --- | --- |
| create | Container created from an amd64 image |
| converge | ok=5, changed=4 (installs cron, places a config file, starts a service, restarts it via a handler) |
| idempotence | changed=0 on the second run |
| verify | `uname -m` is `x86_64`, PID 1 is `systemd` (translated by `rosetta`), `systemctl is-active cron` is `active` |

Pitfalls in the setup:

- With the macOS system Python 3.9 only old versions (Ansible 2.15 / Molecule 6.0) install. Create a virtualenv with Homebrew's Python 3.13.
- The Podman driver has no setting for amd64. `extra_opts` are options for podman itself and do not reach `--platform`. Build an amd64-only image with `podman build --platform linux/amd64` and use it with `pre_build_image: true`.
- Molecule core (array) and the Podman driver (object) disagree on the schema of `tmpfs`, so either form fails validation. With `systemd: always` podman mounts `/run` and `/tmp` as tmpfs automatically, so leave it out.

### Local CI (formerly Agent CI) + podman

(Before the fix) **The job succeeded, but the `run-local-ci` command never noticed it had finished and kept waiting.** The official runner completed all steps in about 10 seconds and the container exited with code 0. It did not return after more than 10 minutes and was stopped with Ctrl+C. run-local-ci (latest on npm), podman 6.2.0, 2026-11-18.

| Step | Result |
| --- | --- |
| `actions/checkout@v4` | Succeeded |
| Show the environment | `aarch64`, Ubuntu 24.04.5 LTS, user `runner` |
| Ansible inside the runner | `ansible localhost -m ping` returns `pong` with ansible-core 2.16.3 |

What was needed to make it run:

- Create `/var/run/docker.sock` with `sudo "$(brew --prefix podman)/bin/podman-mac-helper" install`. Local CI always mounts this path into the runner, so passing podman's Mac-side socket via `LOCAL_CI_DOCKER_HOST` fails at mount time.
- Upstream's automatic build of `.github/local-ci.Dockerfile` calls the `docker` CLI directly and fails, so the image has to be built with podman first and passed via `LOCAL_CI_RUNNER_IMAGE`. The fork builds it through the Podman API instead (see below).
- In a repository without a git remote, `GITHUB_REPO=owner/repo` is required.
- The runner runs as arm64 (GitHub's `ubuntu-latest` is x86_64).

**Cause and fix**: a combination of two problems in podman and Local CI. Local CI moves on when either "the follow log stream closes" or "`container.wait()` returns".

| Side | Problem | How it was checked |
| --- | --- | --- |
| podman 6.2.0 | `wait()` returns after about 3 seconds, but the `logs?follow=true` stream stays open after the container exits (Docker closes it) | A dockerode 5.0.1 reproduction script. It stayed open for 30 seconds regardless of TTY or the order of `wait()` |
| Local CI 0.18.1 | It destroys the stream once `wait()` returns, but Node.js's `readline`, which it uses to decide, does not `close` on `destroy()`, so that safeguard has no effect | The source (`dist/runner/local-job.js`) and behaviour on Node.js 22 / 25 / 26.13.1 |

A one-line patch that also calls `rl.close()` when `wait()` returns fixed it. **With the patch, Local CI completed the same workflow in 5 seconds and exited by itself with `✓ 1 passed`, exit 0.**

```
containerWaitPromise.then(() => {
  rawStream.destroy?.();
  rl.close(); // added
})
```

Node.js 26.13.1 gave the same result: without the patch it had not finished after 90 seconds (stopped), with the patch it finished in 5 seconds with `✓ 1 passed`, exit 0.

### Running the fork under Podman

**With the fork's `parity-and-podman`, Local CI's own full test suite (`pnpm local-ci-dev run --all`) passes 51 of 52 workflows on macOS Podman.** The one failure, the linux-x64 build in `native-binaries`, is a cross-compile that cannot link on an arm64 host. The same suite on GitHub also gives 51 of 52. Verified 2026-11-21.

| Symptom | Cause | Fix in the fork |
| --- | --- | --- |
| Nested Local CI hangs or cannot reach its emulation server | Container detection only checked `/.dockerenv`; Podman creates `/run/.containerenv` instead | Check both files (CLI, emulation server, Rust launcher, scripts) |
| Steps that unpack tar archives fail | The Podman machine's virtiofs rejects the temporary mode-000 files GNU tar creates | Mount a tmpfs on `/home/runner/_work/_temp` when the engine is Podman |
| A custom runner image (`.github/local-ci.Dockerfile`) is built but never found | The docker CLI's buildx `docker-container` builder does not load the image into Podman | Build through the engine API (dockerode `buildImage`) when the engine is Podman |
| Nested docker / Local CI fails with `connect EACCES /var/run/docker.sock` | SELinux in the Podman machine denies the job container (`container_t`) a connection to the Podman service (`container_runtime_t`) | Start job containers with `label=disable` when the engine is Podman |

**`label=disable` is kept on purpose instead of a custom SELinux type.** A custom type (`container_t` plus permission to connect to the socket) would keep file-access confinement and MCS separation. But any job that can reach the API socket can start a privileged container, so both options give a job root-level access to the Podman machine and the home folder it mounts. That small gain did not justify maintaining a policy module loaded into every machine. Without `label=disable`, 10 nested tests failed with `EACCES` (2026-11-21).

What still needs setting up: `/var/run/docker.sock` via `podman-mac-helper` (above). Tests that only work on a matching host, such as macOS VM jobs without `tart` or a different CPU architecture, are skipped automatically with a reason.

### Differences from the real GitHub Actions (parity comparison)

To see how closely Local CI matches the real thing, the same probe workflow is run both on GitHub and in Local CI and the results are compared. The workflow writes the environment, contexts, expression results and data passed between jobs to the log as JSON; a comparison script splits the differences into "needs review" and "known differences" (each with a reason and a link to the documentation that explains it). It runs automatically every Monday on GitHub Actions and commits the report to the public repository [playground050/local-ci-parity](https://github.com/playground050/local-ci-parity) (`reports/gha/`).

What is checked: environment variables; the github / runner / job / steps / needs / strategy / matrix contexts; `toJSON`; step- and job-level `continue-on-error`; `if: always()` jobs after a failure; outputs of failed jobs; step `if:` conditions; matrices (Cartesian product, include, exclude, matrices built from a previous job's outputs, letting only some combinations fail); expression functions and operators; GITHUB_ENV / GITHUB_PATH and env precedence; shell and working-directory; services; actions/cache; reusable-workflow inputs and outputs; job-level if: / runs-on / env / matrix expressions.

The first comparison (Local CI 0.18.1) found many differences that the documentation did not mention, as well as behaviour that contradicted features the documentation lists as supported. They were fixed in a fork ([playground050/local-ci](https://github.com/playground050/local-ci), branch `parity-and-podman`) and each fix was checked against the real GitHub Actions.

| Fix | Behaviour before the fix |
| --- | --- |
| Hang with Podman | The command never returns after the job finishes (#403) |
| `github.sha` etc. | `0000…` or `local/repo` in step `env:` / `run:` |
| `always()` / `failure()` jobs after a failure | Every later job is aborted once a job fails; `needs.<job>.result` is always `success` |
| `toJSON(github)`, `toJSON(needs)`, … | Empty |
| Outputs of failed jobs | Not passed to later jobs |
| Step- and job-level `continue-on-error` | Not supported (the job fails, and so does the run) |
| `GITHUB_REF_NAME`, `GITHUB_WORKFLOW`, … | Environment variables missing |
| Step `env:` | Leaks into the other steps |
| `steps.*` / `job.*` contexts | Empty inside `run:` and `env:` |
| Step `if:` on matrix / needs / strategy | Evaluated against empty values; steps are silently skipped (or run) |
| Matrix `include` / `exclude` | Treated as extra axes: exclusions do not apply and additions are missing |
| Matrices built from a previous job's outputs | A single job runs with empty values |
| Types of matrix values | Booleans and numbers become strings |
| Values written to `GITHUB_ENV` | Lose to workflow / job `env:`, and `${{ env.X }}` in steps does not see them |
| `}}` inside a string in an expression (`format('{{x}}')` etc.) | The expression ends there |
| `true == 1`, `0xff`, `a[1]`, `.*` | Wrong or empty results inside steps |
| `hashFiles` | Different algorithm; zeros instead of an empty string when nothing matches |
| Service `ports: [6379]` (container port only) | The job fails to start |
| `needs` after a job that calls a reusable workflow | Also lists the called workflow's jobs |
| number / boolean inputs of reusable workflows | Become strings |
| Cache `restore-keys` | No prefix match |
| Job if: | Barely parsed: github.event_name == 'push', true == 1 and case-insensitive comparisons are false; no implicit success() && for conditions without a status function |
| Matrix fail-fast and max-parallel | Remaining legs keep starting after a leg fails; max-parallel is ignored |
| Nested runs under Podman | Hang, tar failures, custom image not found, EACCES on the API socket (see "Running the fork under Podman") |

After the fixes the report shows "0 needing review". All remaining differences are understood:

- By design: the execution environment (a minimal Ubuntu 24.04 container; add tools with `.github/local-ci.Dockerfile`), `actions/checkout` copies the local working directory (history of one commit), events are not reproduced (always treated as push), the GitHub API is answered by an internal emulation server, much of the `github` context is fixed values
- Values that cannot be known locally: numeric IDs such as `GITHUB_REPOSITORY_ID`, `job.workflow_ref`, …
- Due to how the comparison is done: on GitHub the probe workflow is called from another workflow, so `GITHUB_WORKFLOW` is the caller

How to use it: Local CI is a tool for finding and fixing failures locally; the final judgement belongs to the real GitHub Actions. When an AI agent uses it, give the agent the list of known differences in its instruction file (AGENTS.md etc.); this keeps it from "fixing" failures that only happen in Local CI.

## Setting up podman

The key is **to set `provider = "applehv"` and `rosetta = true` in containers.conf**. podman 6's default on macOS is libkrun, and the environment variable `CONTAINERS_MACHINE_PROVIDER` is read per command, so forgetting it puts you back on libkrun. Whether Rosetta is used is decided by the containers.conf value at every start (`CONTAINERS_MACHINE_ROSETTA` is not read).

1. Install what is needed.

   ```
   brew install podman
   softwareupdate --install-rosetta --agree-to-license
   ```
2. Add to `~/.config/containers/containers.conf` (if a `[machine]` section exists, add only the two lines under it).

   ```
   [machine]
   provider = "applehv"
   rosetta = true
   ```
3. Remove the old machine created with libkrun and create it again, sharing only the folder your repositories live in (here `~/work`). Without `--volume`, the machine shares `/Users` (every user's home), `/private` and `/var/folders` with the VM.

   ```
   podman machine rm -f
   CONTAINERS_MACHINE_PROVIDER=libkrun podman machine rm -f 2>/dev/null
   podman machine init --volume "$HOME/work:$HOME/work"
   podman machine start
   ```
4. Check. Success means `VM TYPE` is `applehv`, `"Rosetta": true`, `rosetta` appears in binfmt, and `~/work` is the only shared folder (`/var/mnt` is Rosetta's own mount).

   ```
   podman machine list
   podman machine inspect | grep -i rosetta
   podman machine ssh "ls /proc/sys/fs/binfmt_misc/"
   podman machine ssh "mount -t virtiofs"
   ```
5. Use the check command from the verification results to confirm that `rosetta` appears in maps.

For Local CI, two more steps. If lines starting with `#` cause errors in zsh, run `setopt interactivecomments`.

- Create `/var/run/docker.sock` with `sudo "$(brew --prefix podman)/bin/podman-mac-helper" install` and restart the machine.
- Add `export LOCAL_CI_WORKING_DIR="$HOME/work/.local-ci"` to your shell profile. Local CI's working directory defaults to a folder under `/var/folders`, which can no longer be mounted once sharing is limited to `~/work`.

**Why share only one folder**: Local CI gives every job the Podman API socket. A job that can reach the socket can start a privileged container, so it can read and write every Mac folder shared with the VM. With the default shares that is your whole home folder (including `~/.ssh` and credentials) and your temp folder; sharing only `~/work` limits it to your repositories. Shared files are accessed with your own Mac user's permissions, so other users' and root's files cannot be changed either way.

## Licences and cost

The chosen setup (podman + Molecule + Local CI) can be used internally at no extra cost. Docker Desktop and OrbStack are the paid options. Confirm the final legal judgement with the responsible team.

| Tool | Licence | Use in a company |
| --- | --- | --- |
| podman | Apache-2.0 | Free |
| Apple `container` | Apache-2.0 | Free |
| Molecule | MIT | Free |
| Local CI / Agent CI | FSL-1.1-MIT (RedwoodJS Inc.) | Internal use is explicitly allowed. Offering it as a competing commercial service is not. Each version becomes MIT after 2 years. Not OSI-approved |
| tart | FSL-1.1-ALv2 (OpenAI) | Internal use allowed. The old Fair Source licence (paid above 100 cores) is gone. The 2-VM limit is Apple's macOS VM restriction |
| act | MIT | Free |
| Docker Desktop | Commercial | Paid for companies with more than 250 employees or more than $10M annual revenue |
| OrbStack | Commercial | Commercial use is $8 per user per month (billed yearly) |

Local CI does not consume GitHub Actions minutes. Self-hosted runners are not billed for GitHub-side minutes either, but if one stays resident, register it as ephemeral and limit it to private repositories.

## Open questions and next steps

**Open questions**

- Does using Rosetta with applehv require the legacy Rosetta (`libRosettaRuntime`) to be installed? On hold: this Mac already has it, so this needs another macOS 27 Mac without it.
- Local CI fixes live in the fork ([playground050/local-ci](https://github.com/playground050/local-ci), `parity-and-podman`). Upstream has not been updated since 2026-09; the exit-detection problem is registered as issue #403 (open). Upstream PRs are limited to collaborators, so reporting via issues is under consideration.
- Does the target x86 package contain kernel modules (`.ko`)? (`dpkg -c <package>.deb | grep '\.ko'`) If so, it cannot be verified with Rosetta.

**Next steps**

- [ ] Roll out the containers.conf settings to the team's Macs
- [ ] Add a Molecule scenario (amd64 Ubuntu) to the target repositories
- [ ] Write a `verify` script that runs lint, check, Molecule and idempotence together and reports open items (later an agent-facing `verify-infra` skill)
- [ ] Prepare a Local CI Dockerfile with python3 for workflows that run Ansible
- [ ] Add custom ansible-lint rules (forbid `ignore_errors` etc.)

## References

- [All Code Is Slop (Except Mine) — Lauren Tan, SpaceXSI (YouTube)](https://www.youtube.com/watch?v=O_zcc6Xl12g)
- [pstack (cursor/plugins)](https://github.com/cursor/plugins/tree/main/pstack)
- [Local CI (redwoodjs/local-ci)](https://github.com/redwoodjs/local-ci), [compatibility table](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md)
- [Fork with fixes (playground050/local-ci, parity-and-podman)](https://github.com/playground050/local-ci/tree/parity-and-podman)
- [Parity report against the real GitHub Actions (playground050/local-ci-parity)](https://github.com/playground050/local-ci-parity/blob/main/reports/gha/latest.md)
- [nektos/act](https://github.com/nektos/act), [Thoughtworks Radar: Act](https://www.thoughtworks.com/radar/tools/act)
- [ChristopherHX/runner.server](https://github.com/ChristopherHX/runner.server)
- [GitHub Docs: self-hosted runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)
- [Molecule](https://github.com/ansible/molecule)
- [Podman Machine with Apple Rosetta (OneUptime)](https://oneuptime.com/blog/post/2026-03-16-podman-machine-apple-rosetta/view)
- [Apple: Running Intel Binaries in Linux VMs](https://developer.apple.com/tutorials/data/documentation/virtualization/running-intel-binaries-in-linux-vms.md)
- [Using Rosetta with Apple container](https://www.starryhope.com/mac/apple-container-linux-on-mac/)
- [OrbStack: Linux machines](https://docs.orbstack.dev/machines), [OrbStack: Licensing](https://docs.orbstack.dev/licensing)
- [Lima: Intel-on-ARM](https://lima-vm.io/docs/config/multi-arch)
- [tart (openai/tart)](https://github.com/openai/tart)
- [Limit on concurrent macOS VMs (Eclectic Light)](https://eclecticlight.co/2022/08/04/virtualisation-on-apple-silicon-macs-8-how-apple-limits-vms/)
- [Docker pricing](https://docker.io/pricing)
