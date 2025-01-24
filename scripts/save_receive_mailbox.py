import argparse
import asyncio
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path

from njs_mywork_tools.mail.client import (DenbunMailClient,
                                          DenbunMailClientOptions)
from njs_mywork_tools.settings import Settings
from njs_mywork_tools.utils.logger import setup_logger

logger = setup_logger(name=__name__, log_file=Path("logs/receive_mail.log"))


def parse_datetime(date_str: str) -> datetime:
    """日付文字列をdatetimeオブジェクトに変換"""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


async def save_receive_mail(start_date: str, end_date: str, keyword: str):
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

        logger.info("メール受信を開始します")
        logger.info(f"期間: {start_date} から {end_date}")
        logger.info(f"キーワード: {keyword}")

        await client.save_receive_mailbox(start_date=start, end_date=end, keyword=keyword)
        logger.info("メール受信が完了しました")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}", exc_info=True)
    finally:
        await client.close()

if __name__ == "__main__":
    # main()
    # start_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    start_datetime = "2025-01-01 00:00:00"
    end_datetime = "9999-12-31 23:59:59"
    asyncio.run(save_receive_mail(start_datetime, end_datetime, "test"))
