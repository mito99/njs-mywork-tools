import asyncio
import json
import logging

import websockets
from surrealdb import Surreal

from njs_mywork_tools.settings import Settings

# SurrealDBのロガーをデバッグレベルで設定
logging.getLogger('surrealdb').setLevel(logging.DEBUG)

# コンソールハンドラを追加して、デバッグ出力を表示
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

settings = Settings()

async def handle_notification(notification):
    print(f"受信した更新: {notification}")

async def main():
    db = Surreal(settings.surrealdb.url)
    try:
        await db.connect()
        await db.use(settings.surrealdb.namespace, settings.surrealdb.database)
        await db.signin({'user': settings.surrealdb.username, 'pass': settings.surrealdb.password})

        # Start a live query
        live_query_id = await db.live("mail_messages")
        print(f"Live query started with ID: {live_query_id}")
        
        while True:
            # サーバーからのデータ受信を待機
            try:
                response = await db.ws.recv() 
                json_data = json.loads(response)
                print(f"Received update: {json_data}")
                # 受信したデータの処理を行う
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed.")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    finally:
        if db.ws and not db.ws.closed:
            await db.kill(live_query_id)
            await db.close()

if __name__ == "__main__":
    asyncio.run(main())
