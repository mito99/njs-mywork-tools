
from typing import List

from playwright.async_api import Page

from njs_mywork_tools.mail.models.message import MailMessage
from njs_mywork_tools.mail.operations.sent_box.persistence import (
    SentBoxPersistenceOperation, SentBoxPersistenceResult)
from njs_mywork_tools.mail.operations.sent_box.search import \
    SentBoxSearchOperation
from njs_mywork_tools.settings import SurrealDBSetting


class SentBoxOperation:
    """送信ボックスに関する操作をまとめるクラス"""
    def __init__(self, page: Page, surrealdb_setting: SurrealDBSetting):
        self.persistence_operation = SentBoxPersistenceOperation(surrealdb_setting)
        self.search_operation = SentBoxSearchOperation(page)
        
    async def persist_message(self, message: MailMessage) -> SentBoxPersistenceResult:
        """メールを永続化する"""
        return await self.persistence_operation.persist_message(message)

    async def search_messages(
        self, start_date, end_date, keyword
    ) -> List[MailMessage]:
        """メールを検索する"""
        return await self.search_operation.search_messages(start_date, end_date, keyword) 