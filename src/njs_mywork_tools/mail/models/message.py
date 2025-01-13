from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class MailMessage:
    """メール情報を表現するデータモデル"""
    
    id: str
    subject: str
    received_at: datetime
    body: str
    sender: str
    to_addresses: List[str] 
    cc_addresses: List[str]
    attachments: List[str]