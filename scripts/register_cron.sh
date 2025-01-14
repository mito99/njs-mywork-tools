#!/bin/bash

# エラー発生時にスクリプトを終了
set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR=$(cd $(dirname $0); pwd)
RECEIVE_MAIL_SCRIPT="${SCRIPT_DIR}/recieve_mail.sh"

# スクリプトに実行権限を付与
chmod +x "$RECEIVE_MAIL_SCRIPT"

# 一時ファイルに現在のcrontabを保存
crontab -l > /tmp/current_crontab 2>/dev/null || true

# すでに登録されているか確認
if grep -q "$RECEIVE_MAIL_SCRIPT" /tmp/current_crontab; then
    echo "すでにcrontabに登録されています"
    rm /tmp/current_crontab
    exit 0
fi

# 5分ごとに実行するcronジョブを追加
echo "*/5 * * * * $RECEIVE_MAIL_SCRIPT" >> /tmp/current_crontab

# 新しいcrontabを登録
crontab /tmp/current_crontab

# 一時ファイルを削除
rm /tmp/current_crontab

echo "cronジョブを登録しました" 