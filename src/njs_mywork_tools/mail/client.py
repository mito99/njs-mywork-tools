import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import (Browser, BrowserContext, Page,
                                  async_playwright)
from utils.logger import setup_logger

from njs_mywork_tools.mail.core.session import SessionManager
from njs_mywork_tools.mail.operations.recieve import (MailRecieveOperation,
                                                      RecieveMessageResult)
from njs_mywork_tools.mail.operations.search import MailSearchOperation
from njs_mywork_tools.settings import Settings


class DenbunMailClient:
    """
    DenbunMailClient is a client for Denbun Mail.
    """
    def __init__(self, setting: Settings):
        self.setting = setting
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session: Optional[SessionManager] = None
        self.search_operation: Optional[MailSearchOperation] = None
        self.recieve_operation: Optional[MailRecieveOperation] = None
        
        # ロガーの初期化
        self.logger = setup_logger(
            name=self.__class__.__name__,
            log_file=Path("logs/denbun_mail.log")
        )

    async def initialize(self):
        """Initialize Playwright resources"""
        self.logger.info("Initializing DenbunMailClient...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.setting.playwright.headless
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.session = SessionManager(self.page, self.setting.denbun)
        self.search_operation = MailSearchOperation(self.page)
        self.recieve_operation = MailRecieveOperation(self.setting)
        self.logger.info("DenbunMailClient initialized successfully")

    async def close(self):
        """Clean up Playwright resources"""
        self.logger.info("Cleaning up Playwright resources...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Cleanup completed")

    async def send_mail(self, to: str, subject: str, body: str):
        """Send mail using Denbun Mail"""
        if not self.session:
            self.logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            self.logger.info(f"Sending mail to: {to}, subject: {subject}")
            await self.session.ensure_logged_in()
            # メール送信の実装をここに追加
        except Exception as e:
            self.logger.error(f"Failed to send mail: {str(e)}", exc_info=True)
            await self.close()
            raise Exception(f"Failed to send mail: {str(e)}")
        else:
            self.logger.info("Mail sent successfully")

    async def search_mail(self, start_date: datetime, end_date: datetime, keyword: str):
        """Search mail using Denbun Mail"""
        if not self.session:
            self.logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            self.logger.info(
                f"Searching mail (start: {start_date}, end: {end_date}, keyword: {keyword})"
            )
            await self.session.ensure_logged_in()
            await self.search_operation.search_messages(
                start_date=start_date, 
                end_date=end_date, 
                keyword=keyword
            )
        except Exception as e:
            self.logger.error(f"Failed to search mail: {str(e)}", exc_info=True)
            await self.close()
            raise Exception(f"Failed to search mail: {str(e)}")
        else:
            self.logger.info("Mail search completed successfully")

    async def receive_mail(self, start_date: datetime, end_date: datetime, keyword: str):
        """Receive mail using Denbun Mail"""
        if not self.session:
            self.logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            self.logger.info(
                f"Starting mail reception (start: {start_date}, end: {end_date}, keyword: {keyword})"
            )
            await self.session.ensure_logged_in()
            messages = self.search_operation.search_messages_iter(
                start_date=start_date, 
                end_date=end_date, 
                keyword=keyword
            )
            async for message in messages:
                result = await self.recieve_operation.recieve_message(message)
                if result == RecieveMessageResult.ALREADY_EXISTS:
                    self.logger.info("Found existing message. Stopping reception.")
                    break
                self.logger.debug(f"Received message: {message.subject}")
                
        except Exception as e:
            self.logger.error(f"Failed to receive mail: {str(e)}", exc_info=True)
            await self.close()
            raise Exception(f"Failed to receive mail: {str(e)}")
        else:
            self.logger.info("Mail reception completed successfully")

async def main():
    setting = Settings()
    client = DenbunMailClient(setting)
    try:
        await client.initialize()
        # await client.send_mail("test@example.com", "test", "test")
        await client.search_mail(datetime(2024, 12, 23), datetime(2024, 12, 25), "test")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}", exc_info=True)
        raise
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
