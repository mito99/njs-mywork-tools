from enum import Enum
from typing import List, Optional
from datetime import datetime
from playwright.async_api import Page

from mail.core.exceptions import MailOperationError
from mail.operations.search import MailSearchOperation
from mail.repository import MailRepository
from mail.models.message import MailMessage
from settings import Settings, SurrealDBSetting


class RecieveMessageResult(Enum):
    """メール受信操作の結果を表すEnum"""
    ALREADY_EXISTS = "already_exists"  # すでに登録済み
    SAVED = "saved"  # 新規保存完了


class MailRecieveOperation:
    """メール受信操作を行うクラス"""
    
    def __init__(self, settings: Settings):
        self.repository = MailRepository(settings.surrealdb)

    async def recieve_message(
        self,
        message: MailMessage
    ) -> RecieveMessageResult:
        # メッセージの存在確認を行い、結果に応じて戻り値を変える
        exists = await self.repository.exists(message)
        if exists:
            return RecieveMessageResult.ALREADY_EXISTS
            
        await self.repository.save(message)
        return RecieveMessageResult.SAVED