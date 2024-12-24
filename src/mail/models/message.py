from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class MailMessage:
    """メール情報を表現するデータモデル"""
    
    id: str
    subject: str
    received_at: datetime
    body: str
    sender: str
    recipients: List[str] 
    attachments: List[str]