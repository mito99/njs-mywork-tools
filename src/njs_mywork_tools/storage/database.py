import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from surrealdb import Surreal

from njs_mywork_tools.settings import Settings, SurrealDBSetting


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

    async def upsert(self, collection: str, data: dict):
        """
        指定されたコレクションにデータをupsertします。
        データのIDが存在する場合は更新、存在しない場合は新規作成を行います。

        Args:
            collection (str): コレクション名
            data (dict): upsertするデータ（idキーを含む必要があります）

        Returns:
            dict: 作成または更新されたレコード
        
        Raises:
            ValueError: データにidキーが含まれていない場合
        """
        if 'id' not in data:
            raise ValueError("データにidキーが必要です")

        existing_record = await self.find_by_id(collection, data['id'])
        
        if existing_record:
            return await self.update(collection, data['id'], data)
        else:
            result = await self.create(collection, data)
            return result

    async def update(self, collection: str, id: str, data: dict):
        """
        指定されたコレクションの特定のレコードを更新します。

        Args:
            collection (str): コレクション名
            id (str): 更新対象のレコードID
            data (dict): 更新するデータ

        Returns:
            dict: 更新されたレコード
        """
        query = f"""
        UPDATE type::thing($collection, $id) 
        CONTENT $data 
        RETURN AFTER
        """
        params = {
            "collection": collection,
            "data": data,
            "id": id
        }
        
        result = await self.query(query, params)
        if result and len(result) > 0 and 'result' in result[0]:
            return result[0]['result']
        return None

    async def find_by_id(self, collection: str, id: str):
        """
        指定されたコレクションから特定のIDのレコードを取得します。

        Args:
            collection (str): コレクション名
            id (str): 取得対象のレコードID

        Returns:
            dict: 取得したレコード。見つからない場合はNone
        """
        query = f"""
        SELECT * 
        FROM type::thing($collection, $id)
        """
        params = {
            "collection": collection,
            "id": id
        }
        
        result = await self.query(query, params)
        if result and len(result) > 0 and 'result' in result[0]:
            return result[0]['result'][0] if result[0]['result'] else None
        return None

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
