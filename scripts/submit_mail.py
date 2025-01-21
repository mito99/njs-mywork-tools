import asyncio
import platform
import warnings
from pathlib import Path

from playwright.async_api import async_playwright

from njs_mywork_tools.mail.client import (DenbunMailClient,
                                          DenbunMailClientOptions)
from njs_mywork_tools.settings import Settings


async def submit_mail():
    setting = Settings()
    options = DenbunMailClientOptions(
        denbun_setting=setting.denbun,
        surrealdb_setting=setting.surrealdb,
        playwright_headless=setting.playwright.headless,
        xlwings_visible=setting.xlwings.visible,
    )
    async with DenbunMailClient(options) as client:
        
        await client.send_mail(
            to_addresses=["mito-h@n-js.co.jp"],
            subject="test",
            body="test",
            attachment=Path("./tests/attendance/data/template.xlsx"),
        )

async def main():
    await submit_mail()

if __name__ == "__main__":
    asyncio.run(main())
