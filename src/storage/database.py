import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
import uuid
from surrealdb import Surreal

from settings import Settings, SurrealDBSetting

class Database:
    
    def __init__(self, settings: SurrealDBSetting):
        self.settings = settings
        self.db = Surreal(self.settings.url)
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        await self.db.connect()
        await self.db.use(namespace=self.settings.namespace, database=self.settings.database)
        await self.db.signin({"user": self.settings.username, "pass": self.settings.password})

    async def close(self):
        await self.db.close()

    async def query(self, query: str, params: dict = {}):
        return await self.db.query(query, params)

    async def create(self, collection: str, data: dict):
        return await self.db.create(collection, data)
    
    @asynccontextmanager
    async def transaction(self):
        try:
            await self.begin()
            yield
            await self.commit()
        except Exception as e:
            await self.rollback()
            self.logger.error(f"Transaction failed: {str(e)}", exc_info=True)
            raise e
            
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
    
    async def begin(self):
        await self.db.query("BEGIN TRANSACTION;")

    async def commit(self):
        await self.db.query("COMMIT TRANSACTION;")
        
    async def rollback(self):
        await self.db.query("CANCEL TRANSACTION;")

if __name__ == "__main__":
    async def main():
        settings = Settings()
        db = Database(settings.surrealdb)
        async with db:
            async with db.transaction():
                mail_message_id = str(uuid.uuid4())
                mail_message = {
                    "id": mail_message_id,
                    "subject": "プロジェクト進捗報告",
                    "received_at": datetime.now(timezone.utc).isoformat(),
                    "body": "先月のプロジェクト進捗について報告します。",
                    "sender": "project_manager@example.com",
                    "recipients": [],
                    "attachments": []
                }
                await db.create("mail_messages", mail_message)

    asyncio.run(main())
