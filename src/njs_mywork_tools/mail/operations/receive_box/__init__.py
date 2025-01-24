"""受信ボックス操作モジュール

このモジュールは、メールの受信ボックスに関する操作を提供します。
"""

from playwright.async_api import Page

from njs_mywork_tools.settings import SurrealDBSetting

from .persistence import ReceiveBoxPersistenceOperation
from .search import ReceiveBoxSearchOperation


class ReceiveBoxOperation:
    """受信ボックスに関する操作をまとめるクラス"""

    def __init__(self, page: Page, surrealdb_setting: SurrealDBSetting):
        self.persistence_operation = ReceiveBoxPersistenceOperation(surrealdb_setting)
        self.search_operation = ReceiveBoxSearchOperation(page)

    async def persist_message(self, message):
        """メールを永続化する"""
        return await self.persistence_operation.persist_message(message)

    async def search_messages(self, start_date, end_date, keyword):
        """メールを検索する"""
        return await self.search_operation.search_messages(start_date, end_date, keyword) 