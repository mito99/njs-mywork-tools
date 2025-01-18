import asyncio

from njs_mywork_tools.mail.client import DenbunMailClient, DenbunMailClientOptions
from njs_mywork_tools.settings import Settings


async def submit_mail():
    setting = Settings()
    options = DenbunMailClientOptions(
        denbun_setting=setting.denbun,
        surrealdb_setting=setting.surrealdb,
        playwright_headless=setting.playwright.headless,
        xlwings_visible=setting.xlwings.visible,
    )
    client = DenbunMailClient(options)
    await client.send_mail(to="mito-h@n-js.co.jp", subject="test", body="test")


if __name__ == "__main__":
    asyncio.run(submit_mail())
