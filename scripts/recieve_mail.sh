#!/bin/bash

# エラー発生時にスクリプトを終了
set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR=$(cd $(dirname $0); pwd)

cd "$SCRIPT_DIR/.."
.venv/bin/python scripts/receive_mail.py

echo "メール受信処理が完了しました"

