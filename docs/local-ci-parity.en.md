# Making Local CI behave like real GitHub Actions — and checking it every week

Last updated: 2026-11-25

[Local CI](https://github.com/redwoodjs/local-ci) (formerly Agent CI) runs GitHub Actions workflows on your own machine. When a workflow passes locally, you want that to mean it will pass on GitHub. Out of the box, that was not always true: expressions, job results, matrices and several contexts behaved differently from GitHub.

I fixed those differences in [a fork](https://github.com/playground050/local-ci/tree/parity-and-podman) and built [a weekly comparison](https://github.com/playground050/local-ci-parity) that runs the same workflow on real GitHub Actions and on Local CI and diffs the results. In the latest run (2026-11-23), **0 differences were unexplained**. 261 values were identical, and the remaining 169 differences all come from 13 documented causes, such as tools that exist only on GitHub's hosted image.

## Why parity matters

Local CI runs the official GitHub Actions runner in a container, with a local stand-in for GitHub's server side. When a step fails, it pauses, so you can fix the problem and rerun just that step instead of pushing and waiting. That loop is fast enough for coding agents to use too.

The fast loop is only worth having if you can trust it. A workflow that passes locally and then fails on GitHub, or the other way round, is worse than no local run at all, because it teaches you to ignore the result. I wanted a number that says how close the two are, and I wanted that number to be checked again every week.

## How the comparison works

The repository [playground050/local-ci-parity](https://github.com/playground050/local-ci-parity) contains a probe workflow. Its jobs record what they can see: environment variables, contexts, expression results, git state, values passed between jobs, matrix legs, service containers, cache hits, and reusable workflow inputs and outputs. Each value is printed as a `PARITY-JSON` line in the log, after secrets and tokens are removed.

Every Monday, a scheduled workflow:

1. runs the probe on GitHub-hosted `ubuntu-latest`,
2. runs the same probe under Local CI (built from the fork) on another `ubuntu-latest` runner, using Docker,
3. compares the two logs value by value and commits a Markdown report.

Probes that are meant to fail, such as a failing matrix leg or a step after a failure, run as a separate workflow run, so the weekly run itself stays green.

The report sorts every difference into one of two groups:

- **Known**: matched by a rule in [`known.json`](https://github.com/playground050/local-ci-parity/blob/main/.github/parity/known.json). Each rule has a reason and points to where the behaviour is documented.
- **Unexplained**: everything else, listed first. An unexplained difference is either a Local CI bug or a difference nobody has classified yet. Once it is understood, it becomes a fix or a new rule.

Values that change on every run, such as timestamps and run IDs, are excluded (39 in the latest run). The weekly counts are kept in [`history.csv`](https://github.com/playground050/local-ci-parity/blob/main/reports/gha/history.csv), and each report starts with what changed since the previous one.

## What I fixed

Each time I added probes, new unexplained differences appeared: 21 after adding matrix probes, 23 after adding expressions, env files, services, cache and reusable workflows, and 12 after adding job-level expressions. Each batch was fixed in the fork until the count was back to 0. The fork now carries 24 behaviour fixes on top of upstream's `main`.

| Area | What was different, and what the fork does now |
| --- | --- |
| Expressions | Step expressions now see the run's `github` context. `toJSON()` serializes whole contexts. `hashFiles()` is computed the same way as the runner. An expression ends at the first `}}` outside a string. Job-level `if:` uses GitHub's expression rules. |
| Job results | Jobs with `always()` or `failure()` run after an upstream failure. `needs.<job>.result` reports the real result, including `skipped`. A step `if:` without a status function implies `success()`. |
| Failure handling | `continue-on-error` works on steps and on jobs. Step outputs of a failed job are kept. |
| Matrices | `include` / `exclude`, matrices built from expressions (including `needs` outputs), matrix values in `runs-on`, `fail-fast` cancelling legs that have not started, and `max-parallel`. The matrix, strategy and needs contexts reach the runner. |
| Contexts and environment | The `steps` and `job` contexts are evaluated at run time. GitHub's `GITHUB_*` step variables are set. `GITHUB_ENV` overrides workflow and job `env`, as it does on GitHub. `run_id`, `run_number` and `run_attempt` are given to the runner. |
| Reusable workflows, services, cache | Called workflows are keyed by the caller in `needs`, and typed inputs keep their types. A service port given as a container port alone is accepted. Cache `restore-keys` match by prefix, newest entry first. |

The fork also adds support for Podman as the container engine, which upstream does not support.

## What is still different, by design

The 169 known differences come from 13 causes. Most come from Local CI running in a minimal container instead of on a GitHub-hosted virtual machine:

- **Hosted-image environment (59)**: variables for preinstalled tools (Android, Java, Go and others) exist only on GitHub's hosted image.
- **Static `github` context (29)**: many `github` values are fixed or empty locally, for example `ref_name` is always `main` and `run_id` is `1`.
- **Container and runner image (38)**: variables set by Local CI's container, and differences between the minimal runner image and the hosted image.
- **Working directory (12)**: `/home/runner/_work` instead of `/home/runner/work`.
- **Services (7)**: Local CI starts service containers itself and forwards their ports to `localhost`, so `job.services` is empty.
- **Other (24)**: a partial `runner` context, the emulated GitHub API, `actions/checkout` copying the local directory (one commit, no branch), events always being `push`, called-workflow fields in the `job` context, the name a called workflow sees in `github.workflow`, and numeric repository IDs.

They matter when a workflow reads these values or relies on a tool that only the hosted image has. The rules do not hide them: every report lists them with their reasons.

## Limits

- The comparison only covers what the probe asks about. A behaviour the probe does not exercise can still differ.
- Events are not reproduced. Workflows that branch on `pull_request`, `schedule` and so on need a test on GitHub.
- Features that only exist on GitHub, such as OIDC, environments and real secrets, are out of scope.
- The weekly comparison runs on Linux x86_64 with Docker. The fork's own test suite also runs on GitHub, and I run it on a Mac with Podman and with Docker Desktop, but those runs are self-tests, not comparisons against GitHub.

## Status upstream

The fork is based on upstream's `main` as of September 2026. Three of the fixes match issues already open upstream: [#393](https://github.com/redwoodjs/local-ci/issues/393) (the `github` context in step expressions), [#394](https://github.com/redwoodjs/local-ci/issues/394) (`needs.result` for skipped jobs) and [#403](https://github.com/redwoodjs/local-ci/issues/403) (hanging under Podman). Upstream only accepts pull requests from collaborators, so I am considering reporting the rest as issues. Local CI is licensed under FSL-1.1-MIT, and the fork keeps that licence.

## Links

- [Fork with the fixes (playground050/local-ci, `parity-and-podman`)](https://github.com/playground050/local-ci/tree/parity-and-podman)
- [Latest parity report](https://github.com/playground050/local-ci-parity/blob/main/reports/gha/latest.md)
- [Comparison repository (playground050/local-ci-parity)](https://github.com/playground050/local-ci-parity)
- [Local CI (redwoodjs/local-ci)](https://github.com/redwoodjs/local-ci) and its [compatibility table](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md)

---

*This article was written with the help of AI (Claude). The author ran the comparisons and reviewed the text.*
