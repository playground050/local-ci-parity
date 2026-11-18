# Local CI parity report 2026-11-18

- where: GitHub Actions (ubuntu-latest, Docker)
- commit: afc8560ca3bbe2cbffd312e53fdc4a299eee56ba
- run: https://github.com/playground050/local-ci-parity/actions/runs/44324052551
- local_ci: github:playground050/local-ci@fixes/all (1052d40)
- local_ci_exit: 1

違い 43、GitHub のみ 122、Local CI のみ 28、一致 78（実行ごとに変わる 38 項目は除外）

## 値が違う（43）

| 項目 | GitHub | Local CI |
| --- | --- | --- |
| `after-soft-fail.job_status` | success | "" |
| `after-soft-fail.soft_fail` | failure/success | / |
| `dependent.needs.probe.result` | success | failure |
| `probe.contexts.github.head_ref` | "" | main |
| `probe.env_github.GITHUB_ACTION` | __run | probe |
| `probe.env_github.GITHUB_API_URL` | https://api.github.com | http://host.docker.internal:40149 |
| `probe.env_github.GITHUB_ARTIFACTS` | /home/runner/work/_temp/_runner_file_commands/artifacts_5ab120d2-c0fa… | /home/runner/_work/_temp/_runner_file_commands/artifacts_135fd297-51a… |
| `probe.env_github.GITHUB_ARTIFACTS_LIST` | /home/runner/work/_temp/_runner_file_commands/artifacts_list_5ab120d2… | /home/runner/_work/_temp/_runner_file_commands/artifacts_list_135fd29… |
| `probe.env_github.GITHUB_ENV` | /home/runner/work/_temp/_runner_file_commands/set_env_5ab120d2-c0fa-4… | /home/runner/_work/_temp/_runner_file_commands/set_env_135fd297-51a0-… |
| `probe.env_github.GITHUB_EVENT_NAME` | workflow_dispatch | push |
| `probe.env_github.GITHUB_EVENT_PATH` | /home/runner/work/_temp/_github_workflow/event.json | /home/runner/_work/_temp/_github_workflow/event.json |
| `probe.env_github.GITHUB_GRAPHQL_URL` | https://api.github.com/graphql | http://host.docker.internal:40149/_graphql |
| `probe.env_github.GITHUB_JOB` | probe | local-job |
| `probe.env_github.GITHUB_OUTPUT` | /home/runner/work/_temp/_runner_file_commands/set_output_5ab120d2-c0f… | /home/runner/_work/_temp/_runner_file_commands/set_output_135fd297-51… |
| `probe.env_github.GITHUB_PATH` | /home/runner/work/_temp/_runner_file_commands/add_path_5ab120d2-c0fa-… | /home/runner/_work/_temp/_runner_file_commands/add_path_135fd297-51a0… |
| `probe.env_github.GITHUB_STATE` | /home/runner/work/_temp/_runner_file_commands/save_state_5ab120d2-c0f… | /home/runner/_work/_temp/_runner_file_commands/save_state_135fd297-51… |
| `probe.env_github.GITHUB_STEP_SUMMARY` | /home/runner/work/_temp/_runner_file_commands/step_summary_5ab120d2-c… | /home/runner/_work/_temp/_runner_file_commands/step_summary_135fd297-… |
| `probe.env_github.GITHUB_WORKSPACE` | /home/runner/work/local-ci-parity/local-ci-parity | /home/runner/_work/local-ci-parity/local-ci-parity |
| `probe.env_github.RUNNER_TEMP` | /home/runner/work/_temp | /home/runner/_work/_temp |
| `probe.env_github.RUNNER_WORKSPACE` | /home/runner/work/local-ci-parity | /home/runner/_work/local-ci-parity |
| `probe.expressions.EXPR_EVENT` | workflow_dispatch | "" |
| `probe.git.branch` | main | afc8560ca3bbe2cbffd312e53fdc4a299eee56ba |
| `probe.git.commit_count` | 10 | 1 |
| `probe.git.last_commit_author` | playground050 | local-ci |
| `probe.git.remote` | https://github.com/playground050/local-ci-parity | http://127.0.0.1/playground050/local-ci-parity |
| `probe.git.status_clean` | true | false |
| `probe.system.locale` | C.UTF-8 | "" |
| `probe.system.os_release` | Ubuntu 26.04.1 LTS | Ubuntu 24.04.5 LTS |
| `probe.system.workspace` | /home/runner/work/local-ci-parity/local-ci-parity | /home/runner/_work/local-ci-parity/local-ci-parity |
| `probe.tools.ansible` | ansible [core 2.21.6] | null |
| `probe.tools.bash` | GNU bash, version 5.3.9(1)-release (x86_64-pc-linux-gnu) | GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu) |
| `probe.tools.curl` | curl 8.18.0 (x86_64-pc-linux-gnu) libcurl/8.18.0 OpenSSL/3.5.5 zlib/1… | curl 8.5.0 (x86_64-pc-linux-gnu) libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.… |
| `probe.tools.docker` | Docker version 29.4.2, build 055a478 | Docker version 29.9.2, build a82e528 |
| `probe.tools.gcc` | gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0 | null |
| `probe.tools.jq` | jq-1.8.1 | jq-1.7 |
| `probe.tools.make` | GNU Make 4.4.1 | null |
| `probe.tools.node` | v24.22.2 | v24.22.1 |
| `probe.tools.pip3` | pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.14) | null |
| `probe.tools.python3` | Python 3.14.4 | Python 3.12.3 |
| `probe.tools.rsync` | rsync  version 3.4.1  protocol version 32 | null |
| `probe.tools.sudo` | sudo-rs 0.2.13-0ubuntu1.2 | Sudo version 1.9.15p5 |
| `probe.tools.xz` | xz (XZ Utils) 5.8.3 | null |
| `probe.tools.zstd` | *** Zstandard CLI (64-bit) v1.5.7, by Yann Collet *** | null |

## GitHub にだけある（122）

| 項目 | GitHub | Local CI |
| --- | --- | --- |
| `dependent.needs.probe.outputs.answer` | 42 | — |
| `probe.contexts.github.action` | __run | — |
| `probe.contexts.github.action_ref` | "" | — |
| `probe.contexts.github.action_repository` | "" | — |
| `probe.contexts.github.api_url` | https://api.github.com | — |
| `probe.contexts.github.artifact_cache_size_limit` | 10 | — |
| `probe.contexts.github.artifacts` | /home/runner/work/_temp/_runner_file_commands/artifacts_e62163ec-28e0… | — |
| `probe.contexts.github.artifacts_list` | /home/runner/work/_temp/_runner_file_commands/artifacts_list_e62163ec… | — |
| `probe.contexts.github.base_ref` | "" | — |
| `probe.contexts.github.env` | /home/runner/work/_temp/_runner_file_commands/set_env_e62163ec-28e0-4… | — |
| `probe.contexts.github.event_name` | workflow_dispatch | — |
| `probe.contexts.github.event_path` | /home/runner/work/_temp/_github_workflow/event.json | — |
| `probe.contexts.github.graphql_url` | https://api.github.com/graphql | — |
| `probe.contexts.github.job` | probe | — |
| `probe.contexts.github.output` | /home/runner/work/_temp/_runner_file_commands/set_output_e62163ec-28e… | — |
| `probe.contexts.github.path` | /home/runner/work/_temp/_runner_file_commands/add_path_e62163ec-28e0-… | — |
| `probe.contexts.github.ref` | refs/heads/main | — |
| `probe.contexts.github.ref_protected` | false | — |
| `probe.contexts.github.ref_type` | branch | — |
| `probe.contexts.github.repositoryUrl` | git://github.com/playground050/local-ci-parity.git | — |
| `probe.contexts.github.repository_visibility` | public | — |
| `probe.contexts.github.secret_source` | <removed> | — |
| `probe.contexts.github.server_url` | https://github.com | — |
| `probe.contexts.github.state` | /home/runner/work/_temp/_runner_file_commands/save_state_e62163ec-28e… | — |
| `probe.contexts.github.step_summary` | /home/runner/work/_temp/_runner_file_commands/step_summary_e62163ec-2… | — |
| `probe.contexts.github.token` | <removed> | — |
| `probe.contexts.github.triggering_actor` | playground050 | — |
| `probe.contexts.github.workflow` | parity-weekly | — |
| `probe.contexts.github.workflow_ref` | playground050/local-ci-parity/.github/workflows/parity-weekly.yml@ref… | — |
| `probe.contexts.github.workspace` | /home/runner/work/local-ci-parity/local-ci-parity | — |
| `probe.contexts.job.status` | success | — |
| `probe.contexts.job.workflow_file_path` | .github/workflows/parity-probe.yml | — |
| `probe.contexts.job.workflow_ref` | playground050/local-ci-parity/.github/workflows/parity-probe.yml@refs… | — |
| `probe.contexts.job.workflow_repository` | playground050/local-ci-parity | — |
| `probe.contexts.runner.environment` | github-hosted | — |
| `probe.contexts.runner.name` | GitHub Actions 1000000189 | — |
| `probe.contexts.runner.temp` | /home/runner/work/_temp | — |
| `probe.contexts.runner.tool_cache` | /opt/hostedtoolcache | — |
| `probe.contexts.runner.workspace` | /home/runner/work/local-ci-parity | — |
| `probe.contexts.steps.out.conclusion` | success | — |
| `probe.contexts.steps.out.outcome` | success | — |
| `probe.contexts.steps.out.outputs.answer` | 42 | — |
| `probe.env_github.ACTIONS_RUNNER_ACTION_ARCHIVE_CACHE` | /opt/actionarchivecache | — |
| `probe.env_github.ACTIONS_RUNNER_RETURN_JOB_RESULT_FOR_HOSTED` | 1 | — |
| `probe.env_github.GITHUB_BASE_REF` | "" | — |
| `probe.env_github.GITHUB_HEAD_REF` | "" | — |
| `probe.env_github.GITHUB_REF_NAME` | main | — |
| `probe.env_github.GITHUB_REF_PROTECTED` | false | — |
| `probe.env_github.GITHUB_REF_TYPE` | branch | — |
| `probe.env_github.GITHUB_REPOSITORY_OWNER` | playground050 | — |
| `probe.env_github.GITHUB_TRIGGERING_ACTOR` | playground050 | — |
| `probe.env_github.GITHUB_WORKFLOW` | parity-weekly | — |
| `probe.env_github.GITHUB_WORKFLOW_REF` | playground050/local-ci-parity/.github/workflows/parity-weekly.yml@ref… | — |
| `probe.env_github.RUNNER_ENVIRONMENT` | github-hosted | — |
| `probe.env_names[ACCEPT_EULA]` | present | — |
| `probe.env_names[ACTIONS_ORCHESTRATION_ID]` | present | — |
| `probe.env_names[ACTIONS_RUNNER_ACTION_ARCHIVE_CACHE]` | present | — |
| `probe.env_names[ACTIONS_RUNNER_RETURN_JOB_RESULT_FOR_HOSTED]` | present | — |
| `probe.env_names[AGENT_TOOLSDIRECTORY]` | present | — |
| `probe.env_names[ANDROID_HOME]` | present | — |
| `probe.env_names[ANDROID_NDK]` | present | — |
| `probe.env_names[ANDROID_NDK_HOME]` | present | — |
| `probe.env_names[ANDROID_NDK_LATEST_HOME]` | present | — |
| `probe.env_names[ANDROID_NDK_ROOT]` | present | — |
| `probe.env_names[ANDROID_SDK_ROOT]` | present | — |
| `probe.env_names[ANT_HOME]` | present | — |
| `probe.env_names[AZURE_EXTENSION_DIR]` | present | — |
| `probe.env_names[BOOTSTRAP_HASKELL_NONINTERACTIVE]` | present | — |
| `probe.env_names[CHROMEWEBDRIVER]` | present | — |
| `probe.env_names[CHROME_BIN]` | present | — |
| `probe.env_names[DOTNET_MULTILEVEL_LOOKUP]` | present | — |
| `probe.env_names[DOTNET_NOLOGO]` | present | — |
| `probe.env_names[DOTNET_SKIP_FIRST_TIME_EXPERIENCE]` | present | — |
| `probe.env_names[EDGEWEBDRIVER]` | present | — |
| `probe.env_names[ENABLE_RUNNER_TRACING]` | present | — |
| `probe.env_names[GECKOWEBDRIVER]` | present | — |
| `probe.env_names[GHCUP_INSTALL_BASE_PREFIX]` | present | — |
| `probe.env_names[GITHUB_ACTOR_ID]` | present | — |
| `probe.env_names[GITHUB_BASE_REF]` | present | — |
| `probe.env_names[GITHUB_HEAD_REF]` | present | — |
| `probe.env_names[GITHUB_REF_NAME]` | present | — |
| `probe.env_names[GITHUB_REF_PROTECTED]` | present | — |
| `probe.env_names[GITHUB_REF_TYPE]` | present | — |
| `probe.env_names[GITHUB_REPOSITORY_ID]` | present | — |
| `probe.env_names[GITHUB_REPOSITORY_OWNER]` | present | — |
| `probe.env_names[GITHUB_REPOSITORY_OWNER_ID]` | present | — |
| `probe.env_names[GITHUB_TRIGGERING_ACTOR]` | present | — |
| `probe.env_names[GITHUB_WORKFLOW]` | present | — |
| `probe.env_names[GITHUB_WORKFLOW_REF]` | present | — |
| `probe.env_names[GOROOT_1_24_X64]` | present | — |
| `probe.env_names[GOROOT_1_25_X64]` | present | — |
| `probe.env_names[GOROOT_1_26_X64]` | present | — |
| `probe.env_names[GRADLE_HOME]` | present | — |
| `probe.env_names[HCA_CLOUD_PROVIDER]` | present | — |
| `probe.env_names[HOMEBREW_CLEANUP_PERIODIC_FULL_DAYS]` | present | — |
| `probe.env_names[HOMEBREW_NO_AUTO_UPDATE]` | present | — |
| `probe.env_names[ImageVersion]` | present | — |
| `probe.env_names[JAVA_HOME]` | present | — |
| `probe.env_names[JAVA_HOME_11_X64]` | present | — |
| `probe.env_names[JAVA_HOME_17_X64]` | present | — |
| `probe.env_names[JAVA_HOME_21_X64]` | present | — |
| `probe.env_names[JAVA_HOME_25_X64]` | present | — |
| `probe.env_names[LANG]` | present | — |
| `probe.env_names[LOGNAME]` | present | — |
| `probe.env_names[MEMORY_PRESSURE_WATCH]` | present | — |
| `probe.env_names[MEMORY_PRESSURE_WRITE]` | present | — |
| `probe.env_names[NVM_DIR]` | present | — |
| `probe.env_names[PIPX_BIN_DIR]` | present | — |
| `probe.env_names[PIPX_HOME]` | present | — |
| `probe.env_names[POWERSHELL_DISTRIBUTION_CHANNEL]` | present | — |
| `probe.env_names[PSModulePath]` | present | — |
| `probe.env_names[RUNNER_ENVIRONMENT]` | present | — |
| `probe.env_names[SELENIUM_JAR_PATH]` | present | — |
| `probe.env_names[SGX_AESM_ADDR]` | present | — |
| `probe.env_names[SHELL]` | present | — |
| `probe.env_names[SWIFT_PATH]` | present | — |
| `probe.env_names[SYSTEMD_EXEC_PID]` | present | — |
| `probe.env_names[USER]` | present | — |
| `probe.env_names[USE_BAZEL_FALLBACK_VERSION]` | present | — |
| `probe.env_names[VCPKG_INSTALLATION_ROOT]` | present | — |
| `probe.env_names[XDG_CONFIG_HOME]` | present | — |
| `probe.env_names[XDG_RUNTIME_DIR]` | present | — |

## Local CI にだけある（28）

| 項目 | GitHub | Local CI |
| --- | --- | --- |
| `probe.contexts.github.head_sha` | — | 0000000000000000000000000000000000000000 |
| `probe.contexts.job` | — | "" |
| `probe.contexts.steps` | — | "" |
| `probe.env_github.ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT` | — | 1 |
| `probe.env_github.RUNNER_MANUALLY_TRAP_SIG` | — | 1 |
| `probe.env_github.RUNNER_REPOSITORY_URL` | — | http://host.docker.internal:40149/playground050/local-ci-parity |
| `probe.env_names[ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT]` | — | present |
| `probe.env_names[ACTIONS_RUNTIME_TOKEN]` | — | present |
| `probe.env_names[AGENT_CI_DTU_HOST]` | — | present |
| `probe.env_names[AGENT_CI_HEAD_SHA]` | — | present |
| `probe.env_names[AGENT_CI_LOCAL]` | — | present |
| `probe.env_names[AGENT_CI_LOCAL_SYNC]` | — | present |
| `probe.env_names[APP_UID]` | — | present |
| `probe.env_names[ASPNETCORE_HTTP_PORTS]` | — | present |
| `probe.env_names[DOTNET_RUNNING_IN_CONTAINER]` | — | present |
| `probe.env_names[FORCE_COLOR]` | — | present |
| `probe.env_names[JOB_STATUS]` | — | present |
| `probe.env_names[LC_CTYPE]` | — | present |
| `probe.env_names[LOCAL_CI_DTU_HOST]` | — | present |
| `probe.env_names[LOCAL_CI_HEAD_SHA]` | — | present |
| `probe.env_names[LOCAL_CI_LOCAL]` | — | present |
| `probe.env_names[LOCAL_CI_LOCAL_SYNC]` | — | present |
| `probe.env_names[OLDPWD]` | — | present |
| `probe.env_names[RUNNER_MANUALLY_TRAP_SIG]` | — | present |
| `probe.env_names[RUNNER_REPOSITORY_URL]` | — | present |
| `probe.env_names[RUNNER_TOKEN]` | — | present |
| `probe.env_names[SOFT_FAIL]` | — | present |
| `probe.env_names[TERM]` | — | present |

