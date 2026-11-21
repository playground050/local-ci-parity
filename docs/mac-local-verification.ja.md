# Mac での Ansible / GitHub Actions ローカル検証環境 調査まとめ

最終更新: 2026-11-22

## 概要と結論

Ansible のロールと GitHub Actions の workflow を Mac 上で検証する環境として、**podman（applehv + Rosetta）を採用する**。macOS 27 の Mac で、x86_64（amd64）の Linux コンテナ（Ubuntu 22.04 / 24.04 / 26.04）が Rosetta で動くことを確認した。

- **Ansible**: lint・check mode に加え、Molecule の Podman ドライバで amd64 のコンテナに適用し、冪等性まで確かめる。
- **GitHub Actions**: 普段の確認は Local CI（旧 Agent CI。公式 runner をローカルで動かす）を、修正を入れた fork で使う。本物との違いは週次の parity 比較で記録し、既知の違い以外は 0 件になった。OIDC など GitHub 側にしかないものはテスト用ブランチ＋ephemeral な self-hosted runner で確かめる。
- **x86**: macOS 27 の Rosetta は x86-64-v3 まで対応する。カーネルモジュールを含むパッケージ だけは QEMU かクラウドの x86 で確かめる。
- **注意**: podman 6 の macOS でのデフォルト（libkrun）は Rosetta 非対応で、QEMU にフォールバックする。containers.conf での設定が必須。

## 背景：検証を中心に据える考え方

出発点は Lauren Tan（SpaceXSI、Grokbot チーム）のトーク「[All Code Is Slop (Except Mine)](https://www.youtube.com/watch?v=O_zcc6Xl12g)」（AI Engineer Code Summit、2026-11-11）。主張は「エージェントに大量のコードを書かせるなら、正しい振る舞いがデフォルトになる環境と検証に投資せよ」。

- 制約の優先順位は、コードベース（設計）→ 静的解析（lint・型）→ 検証（実行時・形式）→ 文章（AGENTS.md 等）。同じ指摘は lint など決定的なチェックに落とす。
- レビューは「検証の証拠（ログ、動画、差分）」を見る作業になる。実績として 1 か月 11,000 PR、revert 率約 0.5% が示された。
- 本人のプラグイン [pstack](https://github.com/cursor/plugins/tree/main/pstack)（MIT、Claude Code 対応）は、作業種別ごとの playbook（手順と完了基準）と検証 skill を提供する。

本調査はこの考え方を Ansible / GitHub Actions に当てはめ、「Mac だけで動かして証拠を取れる環境」を探したもの。Ansible では特に、pstack の原則「Make Operations Idempotent」（2 回実行して同じ状態に収束するか）がそのまま当てはまる。

## GitHub Actions のローカル検証

普段のループは **Local CI**、GitHub 側にしかない機能の最終確認は **self-hosted runner** の 2 段構えにする。手段は「runner が本物か」「GitHub のサーバー側が本物か」で 3 系統に分かれる。

| 手段 | runner | サーバー側 | push | 向き不向き |
| --- | --- | --- | --- | --- |
| [Local CI](https://github.com/redwoodjs/local-ci)（redwoodjs） | 公式 | ローカルで模倣 | 不要 | 失敗したステップで一時停止し、直してそのステップだけ再実行できる。エージェント向け。0.x 系で初期段階 |
| self-hosted runner（ephemeral） | 公式 | GitHub.com | 必要 | OIDC、environment、本物の secret まで確かめられる。Docker の action を使うなら Linux 上で動かす |
| [act](https://github.com/nektos/act) | 再実装 | 模倣 | 不要 | 最も普及。`workflow_run` や GitHub API を呼ぶ action は差が出る |
| [wrkflw](https://github.com/bahdotsh/wrkflw) | 再実装 | 模倣 | 不要 | act に近い代替 |
| [runner.server](https://github.com/ChristopherHX/runner.server) | 公式の fork | ローカルで模倣 | 不要 | Local CI と同じ発想の先駆け。最終更新 2024 年 |

静的チェックとして `actionlint`（構文・式・shellcheck）と `zizmor`（セキュリティ）を常に先に回す。

**Local CI を使うときの注意**

- デフォルトの runner イメージ（`ghcr.io/actions/actions-runner`）には `python3` がない。Ansible を動かす workflow には独自の Dockerfile が必要。
- Docker API が必要。podman では `podman-mac-helper install` で `/var/run/docker.sock` を用意する（検証済み。詳細は「Local CI＋ podman」）。
- Mac 上のコンテナは基本 ARM64。GitHub の `ubuntu-latest` は x86_64 なので、`amd64` 前提のステップは差が出る。

## Ansible のローカル検証

1 つのテストでは全部拾えないので、速い層から順に回す。中心は [Molecule](https://github.com/ansible/molecule)（v26.6.0、使い捨てのインスタンスに適用→検証→破棄）。

| 層 | 手段 | わかること |
| --- | --- | --- |
| 静的 | `yamllint`、`ansible-lint`、`ansible-playbook --syntax-check` | 書き方の誤り、非推奨の書き方 |
| 差分 | `--check --diff` | 変更の予測。`command` / `shell` は予測できない |
| 実適用 | Molecule（Podman ドライバ） | amd64 のコンテナに実際に適用した結果 |
| 冪等性 | Molecule の idempotence | 2 回目の実行が `changed=0` になるか |
| 本物に近い環境 | tart の Linux VM、クラウドの VM | systemd、sysctl、再起動などコンテナで再現しにくいもの |

**決定的チェックに落とす候補**（トークの考え方を適用）

- `ignore_errors: yes`、`failed_when: false` で失敗を黙らせる書き方を ansible-lint のカスタムルールで禁止する。
- `amd64` / `x86_64` を含む URL を `ansible_architecture` で分岐せずに使うタスクを検出する。
- GitHub Actions 側では `continue-on-error: true` を同様に扱う。

pstack の playbook のうち、Investigation / Bug fix / Refactoring / Feature / Opening a PR / Babysit はそのまま使える。マージまで自動で進む Autopilot-full / Shipping は、マージが本番適用に直結しうるインフラでは使わない。また「playbook」は Ansible の用語と重なるので、依頼時は「Ansible の playbook `site.yml`」のように明示する。

## Mac で x86 Linux を扱う

ユーザー空間だけで完結するパッケージなら、**Rosetta でネイティブに近い速さ**で扱える。カーネルごと x86 が必要な場合だけ QEMU か本物の x86 を使う。

| 方式 | 仕組み | 速さ | 動かないもの |
| --- | --- | --- | --- |
| Rosetta | ARM64 カーネルの上で x86_64 のユーザー空間を変換して実行 | ネイティブに近い | カーネルモジュール・DKMS・ドライバ、32 ビット x86、AVX-512（x86-64-v4） |
| QEMU フルエミュレーション | x86 のカーネルごと命令を変換 | ネイティブの約 1/3。M6 でも比率はほぼ同じ | ほぼなし（遅いだけ） |
| 本物の x86 | クラウド VM、GitHub のホストランナー | 速い | なし（手元では完結しない） |

**Rosetta を使えるツール**: podman（applehv のときのみ）、Apple `container`（デフォルトで有効）、Colima / Lima（`--vz-rosetta`）、OrbStack（`orb create --arch amd64`、商用は有料）、tart（`tart run --rosetta=<tag>`、ARM の Linux VM 内で x86 バイナリを実行）。

**QEMU を使うツール**: Lima（`arch: "x86_64"`）、Colima（`--arch x86_64`）、UTM。

**macOS 27 での変化**: Linux 向けの x86 変換が OS に組み込まれた（`/Library/Apple/usr/libexec/oah/RosettaLinux`）。Mac アプリ向け Rosetta は macOS 28 で縮小されるが、Apple は Linux VM 内の x86 実行は継続するとしている。この Mac（macOS 27）では x86-64-v3 まで使えることを確認した（次章）。

**tart** は Apple Silicon 用の macOS / Linux VM ツール（現在は `openai/tart`、FSL-1.1-ALv2）。Linux VM も ARM 版のみ。macOS VM の同時実行 2 台までという上限は tart ではなく Apple のライセンスによるもの。

## 検証結果（この Mac、macOS 27）

**macOS 27 の Rosetta は x86-64-v3 に対応し、amd64 の Ubuntu が動く。** podman はデフォルトの libkrun では QEMU になり、applehv に切り替えて Rosetta で動いた。2026-11-18 に実施。

| 条件 | 変換の仕組み（確認方法） | 結果 |
| --- | --- | --- |
| podman 6.2.0、libkrun（デフォルト） | binfmt に `qemu-x86_64` のみ。`"Rosetta": false` | QEMU。この状態では Rosetta の判定に使えない |
| 同上、Rosetta を追加インストールして作り直し | 変化なし | libkrun は常に Rosetta 非対応（ソースで確認） |
| Apple `container` 1.7.1（`--arch amd64`） | `/proc/self/maps` に `/run/rosetta/rosetta` | Ubuntu 22.04 / 24.04 / 26.04 で `x86-64-v3 (supported, searched)` |
| podman 6.2.0、applehv + `rosetta = true` | binfmt に `rosetta`、maps に `/var/mnt/rosetta` | Ubuntu 22.04 / 24.04 / 26.04 で `x86-64-v3 (supported, searched)` |

判定に使ったコマンド（x86 の変換役が Rosetta か QEMU かを maps で見る。速度だけでは判断しない）:

```
podman run --rm --platform linux/amd64 docker.io/library/ubuntu:24.04 \
  sh -c 'grep -i -E "rosetta|qemu" /proc/self/maps | head -2; /lib64/ld-linux-x86-64.so.2 --help | grep -i "x86-64-v"'
```

注意点:

- QEMU は x86-64-v3 に対応しているので、QEMU で動いていると Rosetta が非対応でも「動いた」ように見える。必ず変換役を確認する。
- macOS 27 の初期状態では `oah/` に `RosettaLinux` しかなかった。`softwareupdate --install-rosetta` で `libRosettaRuntime` 等が追加された。applehv がこれを必要とするかは未確認。
- Apple `container` 1.7.1 には Rosetta を無効にするオプションがなく（`--rosetta` は有効化のみ）、QEMU との速度比較はできていない。参考値: 300 万回のシェルループで約 8 秒（起動含む）。

### Ubuntu（amd64）

**Ubuntu 22.04 / 24.04 / 26.04 の amd64 イメージも、podman（applehv + Rosetta）で動く。** いずれも maps に `/var/mnt/rosetta` があり、x86-64-v3 まで対応。Ubuntu は標準で x86-64 の基本レベルしか要求しない。

| イメージ | バージョン | glibc | 変換 | x86-64 レベル |
| --- | --- | --- | --- | --- |
| `ubuntu:26.04` | Ubuntu 26.04.1 LTS | 2.43 | Rosetta | v2・v3 対応、v4 非対応 |
| `ubuntu:24.04` | Ubuntu 24.04.5 LTS | 2.39 | Rosetta | v2・v3 対応、v4 非対応 |
| `ubuntu:22.04` | Ubuntu 22.04.5 LTS | 2.35 | Rosetta | v2・v3 対応、v4 非対応 |

`uname -m` は全て `x86_64`、`dpkg --print-architecture` は全て `amd64`。`ubuntu:24.04` で `apt-get install curl python3` が成功した（exit 0、curl 8.5.0 x86_64-pc-linux-gnu、Python 3.12.3、所要約 18 秒）。Ansible の対象として使える。

### Rosetta と QEMU の速度差

**Rosetta はネイティブの 1.1〜3.9 倍、QEMU は 3〜17 倍の時間がかかる。** シェルのような分岐の多い処理では Rosetta が QEMU の約 9 倍速い。Apple M4、macOS 27.2.1、podman 6.2.0（applehv）、`ubuntu:24.04`、2026-11-18 に計測。

| 処理 | arm64 ネイティブ | amd64 + Rosetta | amd64 + QEMU |
| --- | --- | --- | --- |
| bash のループ 300 万回 | 3.86 秒 | 7.63 秒（2.0 倍） | 67.49 秒（17.5 倍） |
| gzip -1、300 MB | 0.77 秒 | 0.83 秒（1.1 倍） | 2.43 秒（3.2 倍） |
| sha256sum、300 MB | 0.16 秒 | 0.62 秒（3.9 倍） | 1.66 秒（10.6 倍） |

倍率は arm64 ネイティブとの比。QEMU は machine 内の `qemu-x86_64-static`（ユーザーモード）をコンテナに渡して明示的に実行した。カーネルごと動かすフルエミュレーションはこれより遅いと考えられる（未計測）。podman 6 の libkrun machine を比較用に作る方法は、`podman machine init` で応答がなくなり中断した。

### Molecule（Podman ドライバ）＋ amd64 ＋ systemd

**`molecule test` が最後まで成功した。** amd64 の Ubuntu 24.04 コンテナで systemd が PID 1 として Rosetta 上で動き、パッケージ導入・設定ファイル配置・サービス起動の role が適用できた。Ansible core 2.22.0、Molecule 26.11.0、molecule-plugins 26.11.0、Python 3.13、2026-11-18 に実施。

| 段階 | 結果 |
| --- | --- |
| create | amd64 イメージからコンテナを作成 |
| converge | ok=5、changed=4（cron 導入、設定ファイル配置、サービス起動、handler で再起動） |
| idempotence | 2 回目は changed=0 |
| verify | `uname -m` が `x86_64`、PID 1 が `systemd`（変換は `rosetta`）、`systemctl is-active cron` が `active` |

設定でつまずいた点:

- macOS 標準の Python 3.9 では Ansible 2.15 / Molecule 6.0 と古い版しか入らない。Homebrew の Python 3.13 で仮想環境を作る。
- Podman ドライバに amd64 を指定する設定はない。`extra_opts` は podman 自体へのオプションで `--platform` は渡せない。`podman build --platform linux/amd64` で amd64 だけのイメージを作り、`pre_build_image: true` で使う。
- `tmpfs` は Molecule 本体（配列）と Podman ドライバ（オブジェクト）でスキーマが食い違い、どちらで書いても検証エラーになる。`systemd: always` なら podman が `/run` と `/tmp` を自動で tmpfs にするので、指定しない。

### Local CI＋ podman

（修正前）**ジョブは成功したが、`run-local-ci` のコマンドが終了を検知できず待ち続けた。** 公式 runner は約 10 秒で全ステップを完了し、コンテナも終了コード 0 で終わった。10 分以上待っても戻らず Ctrl+C で止めた。run-local-ci（npm 最新版）、podman 6.2.0、2026-11-18 に実施。

| ステップ | 結果 |
| --- | --- |
| `actions/checkout@v4` | 成功 |
| 環境の表示 | `aarch64`、Ubuntu 24.04.5 LTS、ユーザー `runner` |
| runner 内で Ansible | ansible-core 2.16.3 で `ansible localhost -m ping` が `pong` |

動かすために必要だったこと:

- `sudo "$(brew --prefix podman)/bin/podman-mac-helper" install` で `/var/run/docker.sock` を作る。Local CI は runner に必ずこのパスを mount するので、`LOCAL_CI_DOCKER_HOST` で podman の Mac 側ソケットを渡すと mount で失敗する。
- upstream の `.github/local-ci.Dockerfile` の自動ビルドは `docker` CLI を直接呼ぶので失敗する。podman で先にビルドし、`LOCAL_CI_RUNNER_IMAGE` で渡す必要がある。fork では Podman の API でビルドするので不要（下記）。
- git remote がないリポジトリでは `GITHUB_REPO=owner/repo` が必要。
- runner は arm64 で動く（GitHub の `ubuntu-latest` は x86_64）。

**原因と修正**: podman と Local CI の 2 つの問題の組み合わせだった。Local CI は「ログの follow ストリームが閉じる」か「`container.wait()` が返る」のどちらかで先に進む作り。

| 側 | 問題 | 確認方法 |
| --- | --- | --- |
| podman 6.2.0 | `wait()` は約 3 秒で返るが、`logs?follow=true` のストリームがコンテナ終了後も閉じない（Docker では閉じる） | dockerode 5.0.1 の再現スクリプト。TTY の有無、`wait()` を呼ぶ順番によらず 30 秒閉じなかった |
| Local CI 0.18.1 | `wait()` が返ったらストリームを `destroy()` する備えがあるが、判定に使う Node.js の `readline` は `destroy()` では `close` しないため効かない | ソース（`dist/runner/local-job.js`）と Node.js 22 / 25 / 26.13.1 での動作 |

`wait()` が返ったときに `rl.close()` も呼ぶ 1 行のパッチで直った。パッチを当てた Local CI は同じワークフローを **5 秒で完了し、`✓ 1 passed`、exit 0 で自分から終了した**。

```
containerWaitPromise.then(() => {
  rawStream.destroy?.();
  rl.close(); // 追加
})
```

Node.js 26.13.1 でも同じ結果だった。パッチなしは 90 秒たっても終了せず（打ち切り）、パッチありは 5 秒で `✓ 1 passed`、exit 0。パッチありでは runner コンテナも自動で削除されたが、打ち切った実行のコンテナは残るので `podman rm` で片付ける。

### fork を Podman で動かす

**fork の `parity-and-podman` では、Local CI 自身のテスト一式（`pnpm local-ci-dev run --all`）が macOS の Podman で 52 本中 51 本成功する。** 失敗する 1 本は `native-binaries` の linux-x64 のビルドで、arm64 のホストではリンクできないクロスコンパイルのため。GitHub 上で同じテストを流しても 52 本中 51 本。2026-11-21 に確認。

| 症状 | 原因 | fork での修正 |
| --- | --- | --- |
| 入れ子の Local CI が止まる、または内部のエミュレーションサーバーに届かない | コンテナ内かどうかを `/.dockerenv` だけで判定していた。Podman は代わりに `/run/.containerenv` を作る | 両方のファイルを確認する（CLI、エミュレーションサーバー、Rust のランチャー、スクリプト） |
| tar を展開するステップが失敗する | Podman machine の virtiofs が、GNU tar が一時的に作るモード 000 のファイルを拒否する | Podman のときは `/home/runner/_work/_temp` に tmpfs をマウントする |
| 独自の runner イメージ（`.github/local-ci.Dockerfile`）をビルドしても見つからない | docker CLI の buildx の `docker-container` ビルダーは、イメージを Podman に読み込まない | Podman のときはエンジンの API（dockerode の `buildImage`）でビルドする |
| 入れ子の docker / Local CI が `connect EACCES /var/run/docker.sock` で失敗する | Podman machine の SELinux が、ジョブのコンテナ（`container_t`）から Podman 本体（`container_runtime_t`）への接続を拒否する | Podman のときはジョブのコンテナを `label=disable` で起動する |

**専用の SELinux の型ではなく、あえて `label=disable` のままにしている。** 専用の型（`container_t` にソケットへの接続の許可を足したもの）なら、ファイルへのアクセス制限と MCS による分離は残る。しかし API ソケットに接続できるジョブは特権コンテナを起動できるので、どちらでもジョブは Podman machine と、そこにマウントされたホームフォルダーに root 相当でアクセスできる。この小さな差のために、machine ごとにポリシーモジュールを読み込んで保守する価値はないと判断した。`label=disable` を外すと、入れ子のテスト 10 本が `EACCES` で失敗した（2026-11-21）。

引き続き必要な準備は、`podman-mac-helper` による `/var/run/docker.sock` の作成（上記）だけ。`tart` のない macOS VM のジョブや CPU アーキテクチャが違うジョブなど、ホストが合わないと動かないテストは、理由付きで自動的にスキップされる。

### 本物の GitHub Actions との違い（parity 比較）

Local CI がどこまで本物と同じに動くかを、同じ調査用 workflow を本物の GitHub と Local CI の両方で実行して比べた。workflow はログに環境・コンテキスト・式の評価・job 間の受け渡しを JSON で出し、比較スクリプトが違いを「要確認」と「既知の違い」（理由と根拠のドキュメント付き）に分けてレポートにする。毎週月曜に GitHub Actions 上で自動実行し、結果をリポジトリにコミットする（公開リポジトリ playground050/local-ci-parity の `reports/gha/`）。

確認している項目: 環境変数、github / runner / job / steps / needs / strategy / matrix コンテキスト、`toJSON`、step と job の `continue-on-error`、失敗後の `if: always()` の job、失敗した job の出力、step の `if:`、matrix（直積、include、exclude、前の job の出力から作る matrix、一部の組み合わせだけ失敗を許す設定）、式の関数と演算子、GITHUB_ENV / GITHUB_PATH と env の優先順位、shell と working-directory、services、actions/cache、再利用ワークフローの inputs / outputs、job の if: / runs-on / env / matrix の式。

最初の比較（Local CI 0.18.1）では、ドキュメントに書かれていない違いや、ドキュメントでは対応済みなのに違う動きが多数見つかった。fork（playground050/local-ci の `parity-and-podman`）で直し、すべて本物と並べて確かめた。

| 修正 | 直す前の動き |
| --- | --- |
| Podman でのハング | ジョブが終わってもコマンドが戻らない（#403） |
| `github.sha` など | step の `env:` / `run:` で `0000…` や `local/repo` になる |
| 失敗後の `always()` / `failure()` の job | 前の job が失敗すると以降の job をすべて打ち切る。`needs.<job>.result` は常に `success` |
| `toJSON(github)` / `toJSON(needs)` など | 空になる |
| 失敗した job の出力 | 後続の job に渡らない |
| step / job の `continue-on-error` | 未対応（job が失敗し、run も失敗） |
| `GITHUB_REF_NAME`、`GITHUB_WORKFLOW` など | 環境変数がない |
| step の `env:` | ほかの step にも入る |
| `steps.*` / `job.*` コンテキスト | `run:` や `env:` の中で空になる |
| step の `if:` で matrix / needs / strategy | 空の値で評価され、step が黙ってスキップ（または実行）される |
| matrix の `include` / `exclude` | 軸の 1 つとして扱われ、除外が効かず追加もされない |
| 前の job の出力から作る matrix | 値が空の job が 1 つだけ動く |
| matrix の値の型 | 真偽値や数値が文字列になる |
| `GITHUB_ENV` に書いた値 | workflow / job の `env:` に負け、step の `${{ env.X }}` にも入らない |
| 式の中の文字列にある `}}`（`format('{{x}}')` など） | 式がそこで切れる |
| `true == 1`、`0xff`、`a[1]`、`.*` | step の中で結果が違う、または空になる |
| `hashFiles` | 計算方法が違う。一致するファイルがないと 0 が並んだ値（本物は空文字） |
| service の `ports: [6379]`（コンテナ側だけ） | ジョブが起動に失敗する |
| 再利用ワークフローを呼ぶ job の後の `needs` | 呼び出し先の job 名も入る |
| 再利用ワークフローの number / boolean の inputs | 文字列になる |
| cache の `restore-keys` | 前方一致で戻せない |
| job の if: | 式をほぼ解釈しない（github.event_name == 'push' が偽、true == 1 や大文字小文字を無視した比較も偽）。状態関数のない条件に success() && が付かない |
| matrix の fail-fast と max-parallel | 1 つの組み合わせが失敗しても残りが始まる。max-parallel は無視される |
| Podman での入れ子の実行 | 止まる、tar の失敗、独自イメージが見つからない、API ソケットへの EACCES（「fork を Podman で動かす」を参照） |

修正後のレポートは「要確認 0」。残る違いはすべて理由が分かっているもの:

- 設計上の違い: 実行環境（最小構成の Ubuntu 24.04 コンテナ。ツールは `.github/local-ci.Dockerfile` で足す）、`actions/checkout` は手元の作業ディレクトリのコピー（履歴は 1 コミット）、イベントは再現しない（常に push 扱い）、GitHub API は内部の代替サーバーが答える、`github` コンテキストの多くは固定値
- 手元では分からない値: `GITHUB_REPOSITORY_ID` などの数値 ID、`job.workflow_ref` など
- 比べ方による違い: 本物では調査用 workflow を別の workflow から呼び出しているため、`GITHUB_WORKFLOW` が呼び出し元になる

使い方の注意: Local CI は手元で失敗を見つけて直すための道具で、最終判断は本物の GitHub Actions に任せる。AI エージェントに使わせる場合は、既知の違いの一覧を指示ファイル（AGENTS.md など）に渡しておくと、Local CI でしか起きない失敗を直そうとする空回りを防げる。

## podman のセットアップ手順

要点は、**containers.conf に `provider = "applehv"` と `rosetta = true` を書くこと**。podman 6 の macOS のデフォルトは libkrun で、環境変数 `CONTAINERS_MACHINE_PROVIDER` は各コマンドごとに読まれるため、付け忘れると libkrun に戻る。Rosetta の有無は起動のたびに containers.conf の値で決まる（`CONTAINERS_MACHINE_ROSETTA` は参照されていない）。

1. 必要なものを入れる。

   ```
   brew install podman
   softwareupdate --install-rosetta --agree-to-license
   ```
2. `~/.config/containers/containers.conf` に追記する（既存の `[machine]` があればその下に 2 行だけ足す）。

   ```
   [machine]
   provider = "applehv"
   rosetta = true
   ```
3. libkrun で作った古い machine を消し、共有するフォルダをリポジトリを置くフォルダ（ここでは `~/work`）だけに絞って作り直す。`--volume` を付けないと、`/Users`（全ユーザーのホーム）、`/private`、`/var/folders` が仮想マシンと共有される。

   ```
   podman machine rm -f
   CONTAINERS_MACHINE_PROVIDER=libkrun podman machine rm -f 2>/dev/null
   podman machine init --volume "$HOME/work:$HOME/work"
   podman machine start
   ```
4. 確認する。`VM TYPE` が `applehv`、`"Rosetta": true`、binfmt に `rosetta` があり、共有が `~/work` だけ（`/var/mnt` は Rosetta 用）なら成功。

   ```
   podman machine list
   podman machine inspect | grep -i rosetta
   podman machine ssh "ls /proc/sys/fs/binfmt_misc/"
   podman machine ssh "mount -t virtiofs"
   ```
5. 検証結果の章の判定コマンドで、maps に `rosetta` が出ることを確かめる。

Local CI を使う場合は、さらに 2 つ準備する。zsh で `#` の行がエラーになる場合は `setopt interactivecomments`。

- `sudo "$(brew --prefix podman)/bin/podman-mac-helper" install` で `/var/run/docker.sock` を作り、machine を再起動する。
- シェルの設定ファイルに `export LOCAL_CI_WORKING_DIR="$HOME/work/.local-ci"` を書く。Local CI の作業フォルダは既定で `/var/folders` の中にあり、共有を `~/work` に絞るとマウントできなくなるため。

**共有を絞る理由**: Local CI はすべてのジョブに Podman の API ソケットを渡す。ソケットに接続できるジョブは特権コンテナを起動できるので、仮想マシンに共有された Mac のフォルダを読み書きできる。既定の共有では、ホーム全体（`~/.ssh` や認証情報を含む）と一時フォルダに届く。`~/work` に絞れば、届く範囲をリポジトリだけにできる。共有したファイルは Mac の自分のユーザーの権限で扱われるので、他のユーザーや root のファイルはどちらの場合も書き換えられない。

## ライセンスと費用

採用する構成（podman + Molecule + Local CI）は、社内利用なら追加費用なしで使える。有料になりうるのは Docker Desktop と OrbStack を使う場合。法的な最終判断は社内の担当部署に確認する。

| ツール | ライセンス | 企業での利用 |
| --- | --- | --- |
| podman | Apache-2.0 | 無料 |
| Apple `container` | Apache-2.0 | 無料 |
| Molecule | MIT | 無料 |
| Local CI | FSL-1.1-MIT（RedwoodJS Inc.） | 社内利用は明示的に許可。競合する商用サービスとしての提供は不可。各版は 2 年後に MIT。OSI 承認ではない |
| tart | FSL-1.1-ALv2（OpenAI） | 社内利用は許可。旧 Fair Source（100 コア超で有料）は廃止。上限 2 台は Apple の macOS VM の制限 |
| act | MIT | 無料 |
| Docker Desktop | 商用 | 従業員 250 人超または年商 1,000 万ドル超の企業は有料 |
| OrbStack | 商用 | 商用は 1 人月 8 ドル（年払い） |

Local CI は GitHub Actions の実行時間を消費しない。self-hosted runner も GitHub 側の実行時間の課金対象外だが、常駐させるなら ephemeral で登録し、private リポジトリに限定する。

## 未確認事項と次の作業

**未確認**

- applehv で Rosetta を使うのに、従来の Rosetta（`libRosettaRuntime`）のインストールが必要か。保留中。この Mac は既に入れてしまったので、従来の Rosetta を入れていない macOS 27 の別の Mac で確認する。
- Local CI の修正は fork（[playground050/local-ci](https://github.com/playground050/local-ci) の `parity-and-podman`）に入れて使っている。上流は 2026-09 から更新が止まっており、終了検知の問題は issue #403（open）として登録済み。上流の PR は collaborator に限られているため、issue での報告を検討する。
- 対象の x86 パッケージにカーネルモジュール（`.ko`）が含まれるか（`dpkg -c`` <パッケージ>.``deb`` | grep '\.ko'`）。含まれれば Rosetta では確かめられない。

**次の作業**

- [ ] チームの Mac に containers.conf の設定を展開する
- [ ] 対象リポジトリに Molecule のシナリオ（amd64 の Ubuntu）を追加する
- [ ] lint、check、Molecule、冪等性をまとめて回し、未確認事項もレポートに書き出す `verify` スクリプト（将来はエージェント向けの `verify-infra` skill）を作る
- [ ] Ansible を動かす workflow 用に、python3 入りの Local CI 用 Dockerfile を用意する
- [ ] ansible-lint のカスタムルール（`ignore_errors` 禁止など）を追加する

## 参考リンク

- [All Code Is Slop (Except Mine) — Lauren Tan, SpaceXSI（YouTube）](https://www.youtube.com/watch?v=O_zcc6Xl12g)
- [pstack（cursor/plugins）](https://github.com/cursor/plugins/tree/main/pstack)
- [nektos/act](https://github.com/nektos/act)、[Thoughtworks Radar: Act](https://www.thoughtworks.com/radar/tools/act)
- [ChristopherHX/runner.server](https://github.com/ChristopherHX/runner.server)
- [GitHub Docs: self-hosted runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)
- [Molecule](https://github.com/ansible/molecule)
- [Podman Machine with Apple Rosetta（OneUptime）](https://oneuptime.com/blog/post/2026-03-16-podman-machine-apple-rosetta/view)
- [Apple: Running Intel Binaries in Linux VMs](https://developer.apple.com/tutorials/data/documentation/virtualization/running-intel-binaries-in-linux-vms.md)
- [Apple container での Rosetta 利用](https://www.starryhope.com/mac/apple-container-linux-on-mac/)
- [OrbStack: Linux machines](https://docs.orbstack.dev/machines)、[OrbStack: Licensing](https://docs.orbstack.dev/licensing)
- [Lima: Intel-on-ARM](https://lima-vm.io/docs/config/multi-arch)
- [tart（openai/tart）](https://github.com/openai/tart)
- [Apple macOS VM の同時実行上限（Eclectic Light）](https://eclecticlight.co/2022/08/04/virtualisation-on-apple-silicon-macs-8-how-apple-limits-vms/)
- [Docker の料金](https://docker.io/pricing)
- [Local CI（redwoodjs/local-ci）](https://github.com/redwoodjs/local-ci)、[互換性の一覧](https://github.com/redwoodjs/local-ci/blob/main/packages/cli/compatibility.md)
- [修正を入れた fork（playground050/local-ci、parity-and-podman）](https://github.com/playground050/local-ci/tree/parity-and-podman)
- [本物との比較レポート（playground050/local-ci-parity）](https://github.com/playground050/local-ci-parity/blob/main/reports/gha/latest.md)
