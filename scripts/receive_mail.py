import argparse
import asyncio
from datetime import datetime

from njs_mywork_tools.mail.client import (DenbunMailClient,
                                          DenbunMailClientOptions)
from njs_mywork_tools.settings import Settings


def parse_datetime(date_str: str) -> datetime:
    """日付文字列をdatetimeオブジェクトに変換"""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

async def receive_mail(start_date: str, end_date: str, keyword: str):
    """メール受信を実行する関数"""
    setting = Settings()
    options = DenbunMailClientOptions(
        denbun_setting=setting.denbun,
        surrealdb_setting=setting.surrealdb,
        playwright_headless=setting.playwright.headless,
        xlwings_visible=setting.xlwings.visible,
    )
    client = DenbunMailClient(options)
    
    try:
        start = parse_datetime(start_date)
        end = parse_datetime(end_date)
        
        print(f"📥 メール受信を開始します")
        print(f"期間: {start_date} から {end_date}")
        print(f"キーワード: {keyword}")
        
        await client.receive_mail(
            start_date=start,
            end_date=end,
            keyword=keyword
        )
        print("✅ メール受信が完了しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
    finally:
        await client.close()

def main():
    parser = argparse.ArgumentParser(description="電文メールを受信するスクリプト")
    parser.add_argument("--start", required=True, help="検索開始日 (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end", required=True, help="検索終了日 (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--keyword", required=True, help="検索キーワード")
    
    args = parser.parse_args()
    asyncio.run(receive_mail(args.start, args.end, args.keyword))

if __name__ == "__main__":
    # main() 
    asyncio.run(receive_mail("2025-01-01 00:00:00", "9999-12-31 23:59:59", "test"))
