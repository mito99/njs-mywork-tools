from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ContactPerson:
    """メールの送信者・受信者情報を表現するデータモデル"""
    
    email: str
    name: str = ""

    def id(self) -> str:
        return self.email
    
    @classmethod
    def from_email_format(cls, email_format: str) -> 'ContactPerson':
        """
        メールの名前形式から ContactPerson を生成するクラスメソッド

        Args:
            email_format (str): メールの名前形式の文字列（例: '"山田太郎" <yamada@example.com>）

        Returns:
            ContactPerson: 生成された連絡先情報
        """
        import re

        pattern = r'(".+"|)\<(.+)\>'
        match = re.match(pattern, email_format)
        
        if not match:
            # マッチしない場合は、メールアドレスをそのまま使用
            return cls(email=email_format.strip(), name="")
        
        name_part, email_part = match.groups()
        
        # 名前部分から引用符を削除
        name = name_part.strip('"').strip() if name_part else ""
        email = email_part.strip()
        
        return cls(email=email, name=name)




@dataclass
class MailMessage:
    """メール情報を表現するデータモデル"""
    
    id: str
    subject: str
    mail_date: datetime
    body: str
    sender: ContactPerson
    to_addresses: List[ContactPerson] 
    cc_addresses: List[ContactPerson]
    attachments: List[str]

