from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from njs_mywork_tools.mail.models.entities import (AttachmentEntity,
                                                   MailMessageEntity,
                                                   RecipientEntity,
                                                   RecipientType)
from njs_mywork_tools.mail.models.message import MailMessage
from njs_mywork_tools.settings import SurrealDBSetting
from njs_mywork_tools.storage import Database


class MailRepository:
    """メールメッセージの永続化を担当するリポジトリ"""
    
    def __init__(self, settings: SurrealDBSetting):
        self.settings = settings
        self.db = Database(settings)
    
    async def save_messages(self, messages: List[MailMessage]) -> None:
        """メールメッセージをデータベースに保存する"""
        for message in messages:
            await self.save(message)
    
    async def save(self, mail_message: MailMessage) -> None:
        """メールメッセージをデータベースに保存する"""
        async with self.db:
            async with self.db.transaction():            

                # 受信者エンティティの作成
                recipient_ids = []
                for recipient in mail_message.to_addresses:
                    id = str(uuid4()).replace("-", "")
                    recipient_entity = RecipientEntity(
                        id=id,
                        mail_message_id=mail_message.id,
                        email=recipient,
                        recipient_type=RecipientType.TO,
                    )
                    # 受信者データを保存し、IDを配列に追加
                    await self.db.create("mail_recipients", recipient_entity.model_dump())
                    recipient_ids.append(id)

                for recipient in mail_message.cc_addresses:
                    id = str(uuid4()).replace("-", "")
                    recipient_entity = RecipientEntity(
                        id=id,
                        mail_message_id=mail_message.id,
                        email=recipient,
                        recipient_type=RecipientType.CC,
                    )
                    await self.db.create("mail_recipients", recipient_entity.model_dump())
                    recipient_ids.append(id)

                # 添付ファイルエンティティの作成
                attachment_ids = []
                for attachment in mail_message.attachments:
                    id = str(uuid4()).replace("-", "")
                    attachment_entity = AttachmentEntity(
                        id=id,
                        mail_message_id=mail_message.id,
                        file_path=attachment,
                    )
                    await self.db.create("mail_attachments", attachment_entity.model_dump())
                    attachment_ids.append(id)

                # メールメッセージエンティティの作成
                message_entity = MailMessageEntity(
                    id=mail_message.id,
                    subject=mail_message.subject.replace(":", "\\:"),
                    received_at=mail_message.received_at.isoformat(),
                    body=mail_message.body,
                    sender=mail_message.sender,
                    recipients=[],
                    attachments=[]
                )
                message_entity_dict = {
                    **message_entity.model_dump(exclude={"recipients", "attachments"}),
                    "recipients": [f"mail_recipients:{id}" for id in recipient_ids],
                    "attachments": [f"mail_attachments:{id}" for id in attachment_ids]
                }
                await self.db.create("mail_messages", message_entity_dict)


    async def find_by_id(self, message_id: str) -> MailMessage:
        """IDによるメールメッセージの検索"""
        async with self.db:
            surql = """
                SELECT *
                FROM type::thing("mail_messages", $id)
                FETCH recipients, attachments
            """
            result = await self.db.query(surql, {"id": message_id})

            data = result[0]['result'][0]
            return self._convert_surreal_result_to_entity(data)

    def _convert_surreal_result_to_entity(self, result: Dict[str, Any]) -> MailMessage:
        if isinstance(result, list):
            result = result[0]
        
        to_recipients = [
            r['email'] for r in result.get('recipients', []) 
            if r['recipient_type'] == RecipientType.TO
        ]
        cc_recipients = [
            r['email'] for r in result.get('recipients', []) 
            if r['recipient_type'] == RecipientType.CC
        ]
        
        attachments = [
            a['file_path'] for a in result.get('attachments', [])
        ]
        
        # メインのMailMessageEntityを構築
        mail_message = MailMessage(
            id=result['id'].split(":")[-1],
            subject=result['subject'],
            received_at= datetime.fromisoformat(result['received_at']),
            body=result['body'],
            sender=result['sender'],
            to_addresses=to_recipients,
            cc_addresses=cc_recipients,
            attachments=attachments
        )
        
        return mail_message

    async def exists(self, mail_message: MailMessage) -> bool:
        """指定されたメールメッセージが既に存在するか確認する"""
        async with self.db:
            surql = """
                SELECT count() as count
                FROM type::thing("mail_messages", $id)
            """
            result = await self.db.query(surql, {"id": mail_message.id})
            
            def safe_get_nested(data, default=0):
                try:
                    return data[0].get('result',{})[0].get('count', default)
                except (IndexError, AttributeError):
                    return default
            
            count = safe_get_nested(result, default=0)
            return count > 0

if __name__ == "__main__":
    import asyncio

    from njs_mywork_tools.settings import Settings
        
    async def main():
        settings = Settings().surrealdb
        repos = MailRepository(settings)
        mail_msg = await repos.find_by_id("INBOX_2678")
        print(mail_msg)

    asyncio.run(main())

