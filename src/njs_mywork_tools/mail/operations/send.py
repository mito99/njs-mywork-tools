from typing import List

from playwright.async_api import Page
from pydantic import BaseModel


class SendMailMessage(BaseModel):
    """メール送信メッセージを表現するデータモデル"""

    to_addresses: List[str]
    cc_addresses: List[str]
    subject: str
    body: str


class MailSendOperation:
    """メール送信操作を行うクラス"""

    def __init__(self, page: Page):
        self.page = page

    async def send_mail(self, message: SendMailMessage):
        """メールを送信する"""

        toolbar = await self.page.locator("#toolbar")
        # ツールバーから「作成」ボタンをクリック
        create_button = toolbar.get_by_role("button", name="作成")
        await create_button.click()
