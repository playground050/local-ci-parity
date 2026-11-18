# Local CI parity report 2026-11-18

- where: GitHub Actions (ubuntu-latest, Docker)
- commit: 1983315f570b658de47d088d9373eb81a4fe2963
- run: https://github.com/playground050/local-ci-parity/actions/runs/44417916729
- local_ci: github:playground050/local-ci@fixes/all (fc1cc22)
- local_ci_exit: 0

**要確認 12** ／ 既知の違い 172 ／ 一致 238（実行ごとに変わる 39 項目は除外）

## 要確認（12）

既知の違い（`.github/parity/known.json`）に当てはまらないもの。Local CI の不具合か、まだ分類していない違い。

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `job-expressions-1.JIF_BOOL_NUM` | success | skipped |
| 値が違う | `job-expressions-1.JIF_FORMAT` | success | skipped |
| 値が違う | `job-expressions-1.JIF_HEX` | success | skipped |
| 値が違う | `job-expressions-1.JIF_INDEX` | success | skipped |
| 値が違う | `job-expressions-1.JIF_NULL` | success | skipped |
| 値が違う | `job-expressions-1.JIF_STR_CI` | success | skipped |
| 値が違う | `job-expressions-2.JIF_BOOL_NUM` | success | skipped |
| 値が違う | `job-expressions-2.JIF_FORMAT` | success | skipped |
| 値が違う | `job-expressions-2.JIF_HEX` | success | skipped |
| 値が違う | `job-expressions-2.JIF_INDEX` | success | skipped |
| 値が違う | `job-expressions-2.JIF_NULL` | success | skipped |
| 値が違う | `job-expressions-2.JIF_STR_CI` | success | skipped |

## 既知の違い（172）

| 理由 | 件数 |
| --- | --- |
| [作業ディレクトリが /home/runner/work ではなく /home/runner/_work（ファイル名の UUID も実行ごとに違う）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md) | 12 |
| [GitHub の API は Local CI 内部の代替サーバー（DTU）が答える](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md#github-api-features-dtu-mock) | 4 |
| [実行環境が GitHub のホストランナーではなく、最小構成の actions-runner コンテナ（Ubuntu 24.04）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/runner-image.md) | 16 |
| [GitHub のホストランナーのイメージにだけある環境変数（Android、Java、Go などのツール類）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/runner-image.md) | 58 |
| Local CI のコンテナと Local CI 自身が設定する環境変数 | 22 |
| [actions/checkout は手元の作業ディレクトリをコピーする（履歴は 1 コミット、ブランチ名なし、未コミット扱い）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md#github-api-features-dtu-mock) | 4 |
| [イベントは再現しない（常に push 扱い、github.event_name は空）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md#workflow-level-keys) | 3 |
| [github コンテキストの多くは固定値か空（ref_name / head_ref は main、run_id は 1 など）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md#expressions--) | 32 |
| [runner コンテキストは os と arch だけ（name、temp、tool_cache などは空）](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md#expressions--) | 5 |
| job コンテキストの workflow_file_path / workflow_ref / workflow_repository（呼び出された workflow の情報）は Local CI では未設定 | 3 |
| 本物では parity-probe.yml を parity-weekly.yml から呼び出す（workflow_call）ため、github.workflow は呼び出し元になる。Local CI では parity-probe.yml を直接実行している（比べ方の違いで、Local CI の問題ではない）。また本物では、呼び出された再利用ワークフローの inputs に parity-weekly.yml の workflow_dispatch の入力（localci_source）も入る | 3 |
| リポジトリやユーザーの数値 ID（GITHUB_REPOSITORY_ID など）は手元では分からない | 3 |
| [Local CI はサービスコンテナを自分で起動し、ジョブの中から localhost:<コンテナのポート> で届くように転送する。runner がサービスを起動しないため job.services は空で、Docker が選ぶホスト側のポート番号もジョブからは見えない。本物ではジョブがホスト上で動くので、届くのは localhost:<ホスト側のポート> だけ](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md) | 7 |

<details><summary>作業ディレクトリが /home/runner/work ではなく /home/runner/_work（ファイル名の UUID も実行ごとに違う）（12）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `probe.env_github.GITHUB_ARTIFACTS` | /home/runner/work/_temp/_runner_file_commands/artifacts_884c086d-9b70… | /home/runner/_work/_temp/_runner_file_commands/artifacts_4353937e-89c… |
| 値が違う | `probe.env_github.GITHUB_ARTIFACTS_LIST` | /home/runner/work/_temp/_runner_file_commands/artifacts_list_884c086d… | /home/runner/_work/_temp/_runner_file_commands/artifacts_list_4353937… |
| 値が違う | `probe.env_github.GITHUB_ENV` | /home/runner/work/_temp/_runner_file_commands/set_env_884c086d-9b70-4… | /home/runner/_work/_temp/_runner_file_commands/set_env_4353937e-89c8-… |
| 値が違う | `probe.env_github.GITHUB_EVENT_PATH` | /home/runner/work/_temp/_github_workflow/event.json | /home/runner/_work/_temp/_github_workflow/event.json |
| 値が違う | `probe.env_github.GITHUB_OUTPUT` | /home/runner/work/_temp/_runner_file_commands/set_output_884c086d-9b7… | /home/runner/_work/_temp/_runner_file_commands/set_output_4353937e-89… |
| 値が違う | `probe.env_github.GITHUB_PATH` | /home/runner/work/_temp/_runner_file_commands/add_path_884c086d-9b70-… | /home/runner/_work/_temp/_runner_file_commands/add_path_4353937e-89c8… |
| 値が違う | `probe.env_github.GITHUB_STATE` | /home/runner/work/_temp/_runner_file_commands/save_state_884c086d-9b7… | /home/runner/_work/_temp/_runner_file_commands/save_state_4353937e-89… |
| 値が違う | `probe.env_github.GITHUB_STEP_SUMMARY` | /home/runner/work/_temp/_runner_file_commands/step_summary_884c086d-9… | /home/runner/_work/_temp/_runner_file_commands/step_summary_4353937e-… |
| 値が違う | `probe.env_github.GITHUB_WORKSPACE` | /home/runner/work/local-ci-parity/local-ci-parity | /home/runner/_work/local-ci-parity/local-ci-parity |
| 値が違う | `probe.env_github.RUNNER_TEMP` | /home/runner/work/_temp | /home/runner/_work/_temp |
| 値が違う | `probe.env_github.RUNNER_WORKSPACE` | /home/runner/work/local-ci-parity | /home/runner/_work/local-ci-parity |
| 値が違う | `probe.system.workspace` | /home/runner/work/local-ci-parity/local-ci-parity | /home/runner/_work/local-ci-parity/local-ci-parity |

</details>

<details><summary>GitHub の API は Local CI 内部の代替サーバー（DTU）が答える（4）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `probe.env_github.GITHUB_API_URL` | https://api.github.com | http://host.docker.internal:36247 |
| 値が違う | `probe.env_github.GITHUB_GRAPHQL_URL` | https://api.github.com/graphql | http://host.docker.internal:36247/_graphql |
| Local CI にだけある | `probe.env_github.RUNNER_REPOSITORY_URL` | — | http://host.docker.internal:36247/playground050/local-ci-parity |
| 値が違う | `probe.git.remote` | https://github.com/playground050/local-ci-parity | http://127.0.0.1/playground050/local-ci-parity |

</details>

<details><summary>実行環境が GitHub のホストランナーではなく、最小構成の actions-runner コンテナ（Ubuntu 24.04）（16）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `probe.system.locale` | C.UTF-8 | "" |
| 値が違う | `probe.system.os_release` | Ubuntu 26.04.1 LTS | Ubuntu 24.04.5 LTS |
| 値が違う | `probe.tools.ansible` | ansible [core 2.21.6] | null |
| 値が違う | `probe.tools.bash` | GNU bash, version 5.3.9(1)-release (x86_64-pc-linux-gnu) | GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu) |
| 値が違う | `probe.tools.curl` | curl 8.18.0 (x86_64-pc-linux-gnu) libcurl/8.18.0 OpenSSL/3.5.5 zlib/1… | curl 8.5.0 (x86_64-pc-linux-gnu) libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.… |
| 値が違う | `probe.tools.docker` | Docker version 29.4.2, build 055a478 | Docker version 29.9.2, build a82e528 |
| 値が違う | `probe.tools.gcc` | gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0 | null |
| 値が違う | `probe.tools.jq` | jq-1.8.1 | jq-1.7 |
| 値が違う | `probe.tools.make` | GNU Make 4.4.1 | null |
| 値が違う | `probe.tools.node` | v24.22.3 | v24.22.1 |
| 値が違う | `probe.tools.pip3` | pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.14) | null |
| 値が違う | `probe.tools.python3` | Python 3.14.4 | Python 3.12.3 |
| 値が違う | `probe.tools.rsync` | rsync  version 3.4.1  protocol version 32 | null |
| 値が違う | `probe.tools.sudo` | sudo-rs 0.2.13-0ubuntu1.2 | Sudo version 1.9.15p5 |
| 値が違う | `probe.tools.xz` | xz (XZ Utils) 5.8.3 | null |
| 値が違う | `probe.tools.zstd` | *** Zstandard CLI (64-bit) v1.5.7, by Yann Collet *** | null |

</details>

<details><summary>GitHub のホストランナーのイメージにだけある環境変数（Android、Java、Go などのツール類）（58）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.env_github.ACTIONS_RUNNER_ACTION_ARCHIVE_CACHE` | /opt/actionarchivecache | — |
| GitHub にだけある | `probe.env_github.ACTIONS_RUNNER_RETURN_JOB_RESULT_FOR_HOSTED` | 1 | — |
| GitHub にだけある | `probe.env_github.RUNNER_ENVIRONMENT` | github-hosted | — |
| GitHub にだけある | `probe.env_names[ACCEPT_EULA]` | present | — |
| GitHub にだけある | `probe.env_names[ACTIONS_ORCHESTRATION_ID]` | present | — |
| GitHub にだけある | `probe.env_names[ACTIONS_RUNNER_ACTION_ARCHIVE_CACHE]` | present | — |
| GitHub にだけある | `probe.env_names[ACTIONS_RUNNER_RETURN_JOB_RESULT_FOR_HOSTED]` | present | — |
| GitHub にだけある | `probe.env_names[AGENT_TOOLSDIRECTORY]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_NDK]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_NDK_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_NDK_LATEST_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_NDK_ROOT]` | present | — |
| GitHub にだけある | `probe.env_names[ANDROID_SDK_ROOT]` | present | — |
| GitHub にだけある | `probe.env_names[ANT_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[AZURE_EXTENSION_DIR]` | present | — |
| GitHub にだけある | `probe.env_names[BOOTSTRAP_HASKELL_NONINTERACTIVE]` | present | — |
| GitHub にだけある | `probe.env_names[CHROMEWEBDRIVER]` | present | — |
| GitHub にだけある | `probe.env_names[CHROME_BIN]` | present | — |
| GitHub にだけある | `probe.env_names[DOTNET_MULTILEVEL_LOOKUP]` | present | — |
| GitHub にだけある | `probe.env_names[DOTNET_NOLOGO]` | present | — |
| GitHub にだけある | `probe.env_names[DOTNET_SKIP_FIRST_TIME_EXPERIENCE]` | present | — |
| GitHub にだけある | `probe.env_names[EDGEWEBDRIVER]` | present | — |
| GitHub にだけある | `probe.env_names[ENABLE_RUNNER_TRACING]` | present | — |
| GitHub にだけある | `probe.env_names[GECKOWEBDRIVER]` | present | — |
| GitHub にだけある | `probe.env_names[GHCUP_INSTALL_BASE_PREFIX]` | present | — |
| GitHub にだけある | `probe.env_names[GOROOT_1_24_X64]` | present | — |
| GitHub にだけある | `probe.env_names[GOROOT_1_25_X64]` | present | — |
| GitHub にだけある | `probe.env_names[GOROOT_1_26_X64]` | present | — |
| GitHub にだけある | `probe.env_names[GRADLE_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[HCA_CLOUD_PROVIDER]` | present | — |
| GitHub にだけある | `probe.env_names[HOMEBREW_CLEANUP_PERIODIC_FULL_DAYS]` | present | — |
| GitHub にだけある | `probe.env_names[HOMEBREW_NO_AUTO_UPDATE]` | present | — |
| GitHub にだけある | `probe.env_names[ImageVersion]` | present | — |
| GitHub にだけある | `probe.env_names[JAVA_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[JAVA_HOME_11_X64]` | present | — |
| GitHub にだけある | `probe.env_names[JAVA_HOME_17_X64]` | present | — |
| GitHub にだけある | `probe.env_names[JAVA_HOME_21_X64]` | present | — |
| GitHub にだけある | `probe.env_names[JAVA_HOME_25_X64]` | present | — |
| GitHub にだけある | `probe.env_names[LANG]` | present | — |
| GitHub にだけある | `probe.env_names[LOGNAME]` | present | — |
| GitHub にだけある | `probe.env_names[MEMORY_PRESSURE_WATCH]` | present | — |
| GitHub にだけある | `probe.env_names[MEMORY_PRESSURE_WRITE]` | present | — |
| GitHub にだけある | `probe.env_names[NVM_DIR]` | present | — |
| GitHub にだけある | `probe.env_names[PIPX_BIN_DIR]` | present | — |
| GitHub にだけある | `probe.env_names[PIPX_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[POWERSHELL_DISTRIBUTION_CHANNEL]` | present | — |
| GitHub にだけある | `probe.env_names[PSModulePath]` | present | — |
| GitHub にだけある | `probe.env_names[RUNNER_ENVIRONMENT]` | present | — |
| GitHub にだけある | `probe.env_names[SELENIUM_JAR_PATH]` | present | — |
| GitHub にだけある | `probe.env_names[SHELL]` | present | — |
| GitHub にだけある | `probe.env_names[SWIFT_PATH]` | present | — |
| GitHub にだけある | `probe.env_names[SYSTEMD_EXEC_PID]` | present | — |
| GitHub にだけある | `probe.env_names[USER]` | present | — |
| GitHub にだけある | `probe.env_names[USE_BAZEL_FALLBACK_VERSION]` | present | — |
| GitHub にだけある | `probe.env_names[VCPKG_INSTALLATION_ROOT]` | present | — |
| GitHub にだけある | `probe.env_names[XDG_CONFIG_HOME]` | present | — |
| GitHub にだけある | `probe.env_names[XDG_RUNTIME_DIR]` | present | — |

</details>

<details><summary>Local CI のコンテナと Local CI 自身が設定する環境変数（22）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| Local CI にだけある | `probe.env_github.ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT` | — | 1 |
| Local CI にだけある | `probe.env_github.RUNNER_MANUALLY_TRAP_SIG` | — | 1 |
| Local CI にだけある | `probe.env_names[ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT]` | — | present |
| Local CI にだけある | `probe.env_names[ACTIONS_RUNTIME_TOKEN]` | — | present |
| Local CI にだけある | `probe.env_names[AGENT_CI_DTU_HOST]` | — | present |
| Local CI にだけある | `probe.env_names[AGENT_CI_HEAD_SHA]` | — | present |
| Local CI にだけある | `probe.env_names[AGENT_CI_LOCAL]` | — | present |
| Local CI にだけある | `probe.env_names[AGENT_CI_LOCAL_SYNC]` | — | present |
| Local CI にだけある | `probe.env_names[APP_UID]` | — | present |
| Local CI にだけある | `probe.env_names[ASPNETCORE_HTTP_PORTS]` | — | present |
| Local CI にだけある | `probe.env_names[DOTNET_RUNNING_IN_CONTAINER]` | — | present |
| Local CI にだけある | `probe.env_names[FORCE_COLOR]` | — | present |
| Local CI にだけある | `probe.env_names[LC_CTYPE]` | — | present |
| Local CI にだけある | `probe.env_names[LOCAL_CI_DTU_HOST]` | — | present |
| Local CI にだけある | `probe.env_names[LOCAL_CI_HEAD_SHA]` | — | present |
| Local CI にだけある | `probe.env_names[LOCAL_CI_LOCAL]` | — | present |
| Local CI にだけある | `probe.env_names[LOCAL_CI_LOCAL_SYNC]` | — | present |
| Local CI にだけある | `probe.env_names[OLDPWD]` | — | present |
| Local CI にだけある | `probe.env_names[RUNNER_MANUALLY_TRAP_SIG]` | — | present |
| Local CI にだけある | `probe.env_names[RUNNER_REPOSITORY_URL]` | — | present |
| Local CI にだけある | `probe.env_names[RUNNER_TOKEN]` | — | present |
| Local CI にだけある | `probe.env_names[TERM]` | — | present |

</details>

<details><summary>actions/checkout は手元の作業ディレクトリをコピーする（履歴は 1 コミット、ブランチ名なし、未コミット扱い）（4）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `probe.git.branch` | main | 1983315f570b658de47d088d9373eb81a4fe2963 |
| 値が違う | `probe.git.commit_count` | 41 | 1 |
| 値が違う | `probe.git.last_commit_author` | playground050 | local-ci |
| 値が違う | `probe.git.status_clean` | true | false |

</details>

<details><summary>イベントは再現しない（常に push 扱い、github.event_name は空）（3）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.contexts.github.event_name` | workflow_dispatch | — |
| 値が違う | `probe.env_github.GITHUB_EVENT_NAME` | workflow_dispatch | push |
| 値が違う | `probe.expressions.EXPR_EVENT` | workflow_dispatch | "" |

</details>

<details><summary>github コンテキストの多くは固定値か空（ref_name / head_ref は main、run_id は 1 など）（32）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.contexts.github.action` | __run | — |
| GitHub にだけある | `probe.contexts.github.action_ref` | "" | — |
| GitHub にだけある | `probe.contexts.github.action_repository` | "" | — |
| GitHub にだけある | `probe.contexts.github.api_url` | https://api.github.com | — |
| GitHub にだけある | `probe.contexts.github.artifact_cache_size_limit` | 10 | — |
| GitHub にだけある | `probe.contexts.github.artifacts` | /home/runner/work/_temp/_runner_file_commands/artifacts_64ade3da-de55… | — |
| GitHub にだけある | `probe.contexts.github.artifacts_list` | /home/runner/work/_temp/_runner_file_commands/artifacts_list_64ade3da… | — |
| GitHub にだけある | `probe.contexts.github.base_ref` | "" | — |
| GitHub にだけある | `probe.contexts.github.env` | /home/runner/work/_temp/_runner_file_commands/set_env_64ade3da-de55-4… | — |
| GitHub にだけある | `probe.contexts.github.event_path` | /home/runner/work/_temp/_github_workflow/event.json | — |
| GitHub にだけある | `probe.contexts.github.graphql_url` | https://api.github.com/graphql | — |
| 値が違う | `probe.contexts.github.head_ref` | "" | main |
| Local CI にだけある | `probe.contexts.github.head_sha` | — | 0000000000000000000000000000000000000000 |
| GitHub にだけある | `probe.contexts.github.job` | probe | — |
| GitHub にだけある | `probe.contexts.github.output` | /home/runner/work/_temp/_runner_file_commands/set_output_64ade3da-de5… | — |
| GitHub にだけある | `probe.contexts.github.path` | /home/runner/work/_temp/_runner_file_commands/add_path_64ade3da-de55-… | — |
| GitHub にだけある | `probe.contexts.github.ref` | refs/heads/main | — |
| GitHub にだけある | `probe.contexts.github.ref_protected` | false | — |
| GitHub にだけある | `probe.contexts.github.ref_type` | branch | — |
| GitHub にだけある | `probe.contexts.github.repositoryUrl` | git://github.com/playground050/local-ci-parity.git | — |
| GitHub にだけある | `probe.contexts.github.repository_visibility` | public | — |
| GitHub にだけある | `probe.contexts.github.secret_source` | <removed> | — |
| GitHub にだけある | `probe.contexts.github.server_url` | https://github.com | — |
| GitHub にだけある | `probe.contexts.github.state` | /home/runner/work/_temp/_runner_file_commands/save_state_64ade3da-de5… | — |
| GitHub にだけある | `probe.contexts.github.step_summary` | /home/runner/work/_temp/_runner_file_commands/step_summary_64ade3da-d… | — |
| GitHub にだけある | `probe.contexts.github.token` | <removed> | — |
| GitHub にだけある | `probe.contexts.github.triggering_actor` | playground050 | — |
| GitHub にだけある | `probe.contexts.github.workflow` | parity-weekly | — |
| GitHub にだけある | `probe.contexts.github.workflow_ref` | playground050/local-ci-parity/.github/workflows/parity-weekly.yml@ref… | — |
| GitHub にだけある | `probe.contexts.github.workspace` | /home/runner/work/local-ci-parity/local-ci-parity | — |
| 値が違う | `probe.env_github.GITHUB_ACTION` | __run | probe |
| 値が違う | `probe.env_github.GITHUB_JOB` | probe | local-job |

</details>

<details><summary>runner コンテキストは os と arch だけ（name、temp、tool_cache などは空）（5）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.contexts.runner.environment` | github-hosted | — |
| GitHub にだけある | `probe.contexts.runner.name` | GitHub Actions 1000000683 | — |
| GitHub にだけある | `probe.contexts.runner.temp` | /home/runner/work/_temp | — |
| GitHub にだけある | `probe.contexts.runner.tool_cache` | /opt/hostedtoolcache | — |
| GitHub にだけある | `probe.contexts.runner.workspace` | /home/runner/work/local-ci-parity | — |

</details>

<details><summary>job コンテキストの workflow_file_path / workflow_ref / workflow_repository（呼び出された workflow の情報）は Local CI では未設定（3）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.contexts.job.workflow_file_path` | .github/workflows/parity-probe.yml | — |
| GitHub にだけある | `probe.contexts.job.workflow_ref` | playground050/local-ci-parity/.github/workflows/parity-probe.yml@refs… | — |
| GitHub にだけある | `probe.contexts.job.workflow_repository` | playground050/local-ci-parity | — |

</details>

<details><summary>本物では parity-probe.yml を parity-weekly.yml から呼び出す（workflow_call）ため、github.workflow は呼び出し元になる。Local CI では parity-probe.yml を直接実行している（比べ方の違いで、Local CI の問題ではない）。また本物では、呼び出された再利用ワークフローの inputs に parity-weekly.yml の workflow_dispatch の入力（localci_source）も入る（3）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `probe.env_github.GITHUB_WORKFLOW` | parity-weekly | parity-probe |
| 値が違う | `probe.env_github.GITHUB_WORKFLOW_REF` | playground050/local-ci-parity/.github/workflows/parity-weekly.yml@ref… | playground050/local-ci-parity/.github/workflows/parity-probe.yml@refs… |
| GitHub にだけある | `reusable-inner.inputs.localci_source` | github:playground050/local-ci@fixes/all | — |

</details>

<details><summary>リポジトリやユーザーの数値 ID（GITHUB_REPOSITORY_ID など）は手元では分からない（3）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| GitHub にだけある | `probe.env_names[GITHUB_ACTOR_ID]` | present | — |
| GitHub にだけある | `probe.env_names[GITHUB_REPOSITORY_ID]` | present | — |
| GitHub にだけある | `probe.env_names[GITHUB_REPOSITORY_OWNER_ID]` | present | — |

</details>

<details><summary>Local CI はサービスコンテナを自分で起動し、ジョブの中から localhost:<コンテナのポート> で届くように転送する。runner がサービスを起動しないため job.services は空で、Docker が選ぶホスト側のポート番号もジョブからは見えない。本物ではジョブがホスト上で動くので、届くのは localhost:<ホスト側のポート> だけ（7）</summary>

| 種類 | 項目 | GitHub | Local CI |
| --- | --- | --- | --- |
| 値が違う | `services.fields` | ["id", "network", "ports"] | [] |
| 値が違う | `services.has_mapped_port` | true | false |
| 値が違う | `services.has_network` | true | false |
| 値が違う | `services.names` | ["redis"] | [] |
| 値が違う | `services.port_differs_from_container` | true | false |
| 値が違う | `services.via_localhost_container_port` | ConnectionRefusedError | +PONG |
| 値が違う | `services.via_localhost_mapped` | +PONG | no-port |

</details>

