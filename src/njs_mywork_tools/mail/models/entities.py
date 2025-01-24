from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RecipientType(str, Enum):
    """受信者タイプ"""
    TO = "to"
    CC = "cc"


class ContactEntity(BaseModel):
    """連絡先エンティティ"""
    id: str
    name: Optional[str] = None

    def email(self) -> str:
        return self.id


class SenderEntity(BaseModel):
    """送信者エンティティ"""
    id: str
    message_id: str
    email: str
    contact: Optional[ContactEntity] = None


class RecipientEntity(BaseModel):
    """受信者エンティティ"""
    id: str
    message_id: str
    email: str
    recipient_type: RecipientType
    contact: Optional[ContactEntity] = None


class AttachmentEntity(BaseModel):
    """添付ファイルエンティティ"""
    id: str
    message_id: str
    file_path: str


class MailMessageEntity(BaseModel):
    """メールメッセージのデータモデル"""
    id: str
    subject: str
    mail_date: str
    body: str
    sender: SenderEntity
    recipients: list[RecipientEntity]
    attachments: list[AttachmentEntity]

