import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.async_api import (Browser, BrowserContext, Page,
                                  async_playwright)
from pydantic import BaseModel

from njs_mywork_tools.mail.core.session import SessionManager
from njs_mywork_tools.mail.operations.recieve import (MailRecieveOperation,
                                                      RecieveMessageResult)
from njs_mywork_tools.mail.operations.search import MailSearchOperation
from njs_mywork_tools.mail.operations.send import (MailSendOperation,
                                                   SendMailMessage)
from njs_mywork_tools.settings import (DenbunSetting, GoogleSheetSetting,
                                       SurrealDBSetting)
from njs_mywork_tools.utils.logger import setup_logger

logger = setup_logger(name=__name__, log_file=Path("logs/denbun_mail.log"))


class DenbunMailClientOptions(BaseModel):
    denbun_setting: DenbunSetting
    surrealdb_setting: SurrealDBSetting
    playwright_headless: bool = False
    xlwings_visible: bool = False


class DenbunMailClient:
    """
    DenbunMailClient is a client for Denbun Mail.
    """

    def __init__(self, options: DenbunMailClientOptions):
        self.options = options
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session: Optional[SessionManager] = None
        self.search_operation: Optional[MailSearchOperation] = None
        self.recieve_operation: Optional[MailRecieveOperation] = None
        self.send_operation: Optional[MailSendOperation] = None

    async def initialize(self):
        """Initialize Playwright resources"""
        logger.info("Initializing DenbunMailClient...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.options.playwright_headless
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.send_operation = MailSendOperation(self.page)
        self.session = SessionManager(self.page, self.options.denbun_setting)
        self.search_operation = MailSearchOperation(self.page)
        self.recieve_operation = MailRecieveOperation(self.options.surrealdb_setting)
        logger.info("DenbunMailClient initialized successfully")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        """Clean up Playwright resources"""
        logger.info("Cleaning up Playwright resources...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Cleanup completed")

    async def send_mail(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        cc_addresses: Optional[List[str]] = [],
        attachment: Optional[Path] = None,
    ):
        """Send mail using Denbun Mail"""
        if not self.session:
            logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            logger.info(f"Sending mail to: {to_addresses}, subject: {subject}")
            await self.session.ensure_logged_in()
            send_message = SendMailMessage(
                to_addresses=to_addresses,
                cc_addresses=cc_addresses,
                subject=subject,
                body=body,
                attachment=attachment,
            )
            await self.send_operation.send_mail(send_message)
        except Exception as e:
            logger.error(f"Failed to send mail: {str(e)}", exc_info=True)
            await self.close()
            raise Exception(f"Failed to send mail: {str(e)}")
        else:
            logger.info("Mail sent successfully")

    async def search_mail(self, start_date: datetime, end_date: datetime, keyword: str):
        """Search mail using Denbun Mail"""
        if not self.session:
            logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            logger.info(
                f"Searching mail (start: {start_date}, end: {end_date}, keyword: {keyword})"
            )
            await self.session.ensure_logged_in()
            await self.search_operation.search_messages(
                start_date=start_date, end_date=end_date, keyword=keyword
            )
        except Exception as e:
            logger.error(f"Failed to search mail: {str(e)}", exc_info=True)
            raise Exception(f"Failed to search mail: {str(e)}")
        else:
            logger.info("Mail search completed successfully")
        finally:
            await self.close()

    async def receive_mail(
        self, start_date: datetime, end_date: datetime, keyword: str
    ):
        """Receive mail using Denbun Mail"""
        if not self.session:
            logger.info("Session not initialized. Initializing...")
            await self.initialize()
        try:
            logger.info(
                f"Starting mail reception (start: {start_date}, end: {end_date}, keyword: {keyword})"
            )
            await self.session.ensure_logged_in()
            messages = self.search_operation.search_messages_iter(
                start_date=start_date, end_date=end_date, keyword=keyword
            )
            async for message in messages:
                result = await self.recieve_operation.recieve_message(message)
                if result == RecieveMessageResult.ALREADY_EXISTS:
                    logger.info("Found existing message. Stopping reception.")
                    break
                logger.debug(f"Received message: {message.subject}")

        except Exception as e:
            logger.error(f"Failed to receive mail: {str(e)}", exc_info=True)
            await self.close()
            raise Exception(f"Failed to receive mail: {str(e)}")
        else:
            logger.info("Mail reception completed successfully")


async def main():
    from njs_mywork_tools.settings import Settings

    setting = Settings()
    options = DenbunMailClientOptions(
        denbun_setting=setting.denbun,
        surrealdb_setting=setting.surrealdb,
        playwright_headless=setting.playwright.headless,
        xlwings_visible=setting.xlwings.visible,
    )
    client = DenbunMailClient(options)
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
