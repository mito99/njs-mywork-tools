from enum import Enum

from njs_mywork_tools.mail.models.message import MailMessage
from njs_mywork_tools.mail.repository import MailRepository
from njs_mywork_tools.settings import SurrealDBSetting


class SentBoxPersistenceResult(Enum):
    """送信ボックスのメール永続化操作の結果を表すEnum"""
    ALREADY_EXISTS = "already_exists"  # すでに登録済み
    SAVED = "saved"  # 新規保存完了
    
    def is_already_exists(self) -> bool:
        return self == SentBoxPersistenceResult.ALREADY_EXISTS
    
    def is_saved(self) -> bool:
        return self == SentBoxPersistenceResult.SAVED

class SentBoxPersistenceOperation:
    """送信ボックスのメール永続化操作を行うクラス"""
    
    def __init__(self, surrealdb_setting: SurrealDBSetting):
        self.repository = MailRepository(surrealdb_setting)

    async def persist_message(
        self,
        message: MailMessage
    ) -> SentBoxPersistenceResult:
        # メッセージの存在確認を行い、結果に応じて戻り値を変える
        exists = await self.repository.exists(message)
        if exists:
            return SentBoxPersistenceResult.ALREADY_EXISTS
            
        # メッセージを永続化する
        await self.repository.save(message)
        return SentBoxPersistenceResult.SAVED