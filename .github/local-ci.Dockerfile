# Local CI の runner イメージ。公式イメージには python3 がないので、調査スクリプト用に追加する。
# （Local CI がこのファイルを見つけて自動でビルドする。Mac 版は LOCAL_CI_RUNNER_IMAGE で上書きする）
FROM ghcr.io/actions/actions-runner:latest
RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends python3 \
 && sudo rm -rf /var/lib/apt/lists/*
