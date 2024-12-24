import asyncio
import uuid
from datetime import datetime, timezone
from surrealdb import Surreal
import pytz

async def main():
    # SurrealDBに接続
    async with Surreal("ws://localhost:8000/rpc") as db:
        # 名前空間とデータベースを選択
        await db.use(namespace="mito", database="njs")
        await db.signin({"user": "njs_user", "pass": "njs_user"})

        # メールメッセージの作成
        mail_message_id = str(uuid.uuid4())
        mail_message = {
            "id": mail_message_id,
            "subject": "プロジェクト進捗報告",
            "received_at": datetime.now(timezone.utc).isoformat(),
            "body": "先月のプロジェクト進捗について報告します。",
            "sender": "project_manager@example.com",
            "recipients": [],
            "attachments": []
        }

        # メールメッセージを登録
        await db.create("mail_messages", mail_message)

        # 受信者の作成と登録
        recipients = [
            {
                "id": str(uuid.uuid4()),
                "mail_message_id": mail_message_id,
                "email": "team_lead@example.com"
            },
            {
                "id": str(uuid.uuid4()),
                "mail_message_id": mail_message_id,
                "email": "developer@example.com"
            }
        ]
        
        for recipient in recipients:
            await db.create("mail_recipients", recipient)

        # 添付ファイルの作成と登録
        attachments = [
            {
                "id": str(uuid.uuid4()),
                "mail_message_id": mail_message_id,
                "file_path": "/path/to/progress_report.pdf"
            }
        ]
        
        for attachment in attachments:
            await db.create("mail_attachments", attachment)

        print("メールデータの登録が完了しました。")

if __name__ == "__main__":
    asyncio.run(main())