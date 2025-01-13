from enum import Enum

from pydantic import BaseModel


class RecipientType(str, Enum):
    TO = "to"
    CC = "cc"

class RecipientEntity(BaseModel):
    id: str
    mail_message_id: str
    email: str
    recipient_type: RecipientType

class AttachmentEntity(BaseModel):
    id: str
    mail_message_id: str
    file_path: str
    
class MailMessageEntity(BaseModel):
    """メールメッセージのデータモデル"""
    id: str
    subject: str
    received_at: str
    body: str
    sender: str
    
    recipients: list[RecipientEntity]
    attachments: list[AttachmentEntity]

