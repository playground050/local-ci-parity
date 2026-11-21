# local-ci parity probe

[Local CI](https://github.com/redwoodjs/local-ci)（旧 Agent CI）が、本物の GitHub Actions とどれだけ違うかを毎週記録するリポジトリ。

同じ調査用 workflow（`.github/workflows/parity-probe.yml`）を本物の GitHub と Local CI の両方で実行し、ログに出した `PARITY-JSON` 行（環境、コンテキスト、git の状態、式の評価、ジョブ間の受け渡しなど）を比べる。トークンなどの値は書き出す前に削除する。

| レポート | 実行する場所 | 比べるもの |
| --- | --- | --- |
| [`reports/gha/latest.md`](reports/gha/latest.md) | GitHub Actions（`parity-weekly.yml`、毎週月曜 09:17 JST） | 本物 vs Local CI on Docker（どちらも ubuntu-latest、x86_64） |
| [`reports/mac/latest.md`](reports/mac/latest.md) | 手元の Mac（launchd） | 本物 vs Local CI on podman（applehv + Rosetta、arm64） |

各フォルダの `history.csv` に週ごとの件数、`YYYY-MM-DD.md` の先頭に前回からの変化がある。

レポートは、Local CI の仕様として分かっている違い（[`.github/parity/known.json`](.github/parity/known.json)、理由と根拠のドキュメント付き）を「既知の違い」にまとめ、それ以外を「要確認」として先に出す。要確認に出たものは、Local CI の不具合か、まだ分類していない違い。調べて仕様だと分かったら `known.json` に足す。

## 調査まとめ

Mac で Ansible と GitHub Actions をローカル検証する環境の調査結果（podman + Rosetta、Molecule、Local CI の修正と Podman での動かし方）。

- [日本語](docs/mac-local-verification.ja.md)
- [English](docs/mac-local-verification.en.md)

## ファイル

- `.github/workflows/parity-probe.yml` … 調査用 workflow（本物と Local CI の両方で実行）
- `.github/workflows/parity-weekly.yml` … GitHub Actions での毎週の比較
- `.github/parity/probe.py` … 環境を調べて `PARITY-JSON` 行を出す
- `.github/parity/emit.py` … 環境変数の値を `PARITY-JSON` 行として出す（matrix などの小さな記録用）
- `.github/parity/compare.py` … 2 つのログを比べて Markdown のレポートを作る
- `.github/parity/known.json` … 既知の違いの一覧（項目名の正規表現と理由）
- `.github/local-ci.Dockerfile` … Local CI の runner イメージに python3 を足す
