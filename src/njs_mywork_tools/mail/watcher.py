import asyncio
import json
import logging
from typing import AsyncGenerator, TypedDict

from surrealdb import Surreal

from njs_mywork_tools.mail.models.entities import MailMessageEntity
from njs_mywork_tools.mail.repository import MailRepository
from njs_mywork_tools.settings import Settings, SurrealDBSetting


class MailChangeEvent(TypedDict):
    action: str
    mail_msg: MailMessageEntity

class MailWatcher:
    
    def __init__(self, db: Surreal, settings: SurrealDBSetting):
        self.db = db
        self.settings = settings
        
    @classmethod
    async def start(cls, settings: SurrealDBSetting):
        db = Surreal(settings.url)
        await db.connect()
        await db.use(settings.namespace, settings.database)
        await db.signin({'user': settings.username, 'pass': settings.password})
        
        return cls(db, settings)

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.db.ws and not self.db.ws.closed:
            await self.db.kill(self.live_query_id)
        await self.db.close()
    
    async def watch_mails(self) -> AsyncGenerator[MailChangeEvent, None]:
        """メールの変更を監視し、更新があった場合にデータを返すasync generator

        Yields:
            MailChangeEvent: 新規作成されたメールデータのID
        """
        
        repos = MailRepository(self.settings)
        
        try:
            # LiveQueryを設定
            self.live_query_id = await self.db.live('mail_messages')
            
            while True:
                if not self.db.ws or self.db.ws.closed:
                    logging.error("WebSocket接続が切断されました")
                    break
                
                try:
                    # WebSocketからデータを待機
                    data = await self.db.ws.recv()
                    result = json.loads(data)
                    
                    # LiveQueryの結果のみを処理
                    if result.get('result') and isinstance(result['result'], dict):
                        result_data = result['result']
                        action = result_data['action']
                        mail_id = result_data['record']
                        mail_msg = await repos.find_by_id(mail_id)
                        yield MailChangeEvent(action=action, mail_msg=mail_msg)
                        
                except Exception as e:
                    logging.error(f"エラーが発生しました。: {e}")
                    break
                
        finally:
            if hasattr(self, 'live_query_id'):
                await self.db.kill(self.live_query_id)
    

if __name__ == "__main__":
    async def main():
        settings = Settings().surrealdb
        watcher = await MailWatcher.start(settings)
        async for mail in watcher.watch_mails():
            print(mail)
    
    asyncio.run(main())
    
