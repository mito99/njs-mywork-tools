import asyncio
from pathlib import Path
from typing import List, Optional

from playwright.async_api import Page
from pydantic import BaseModel


class SendMailMessage(BaseModel):
    """メール送信メッセージを表現するデータモデル"""

    to_addresses: List[str]
    cc_addresses: List[str]
    subject: str
    body: str
    attachment: Optional[Path] = None

class MailSendOperation:
    """メール送信操作を行うクラス"""

    def __init__(self, page: Page):
        self.page = page

    async def send_mail(self, message: SendMailMessage) -> None:
        """メールを送信する"""

        toolbar = self.page.locator("#toolbar")
        # ツールバーから「作成」ボタンをクリックすると送信用のポップアップが起動する
        async with self.page.expect_popup() as popup_info:
            await asyncio.sleep(1)
            create_button = toolbar.get_by_role("button", name="作成")
            await create_button.click()
        
        popup = await popup_info.value
        await popup.wait_for_load_state('networkidle')
        
        # 送信情報を入力
        # 宛先を入力
        await popup.fill("input#mail-edit-to", message.to_addresses[0])
        await popup.keyboard.press("Tab")
        
        # CCアドレスを追加する
        if message.cc_addresses:
            await popup.click("span#mail-edit-add_cc")
            await popup.wait_for_selector("input#mail-edit-cc", state='visible')
            await popup.fill("input#mail-edit-cc", message.cc_addresses[0])
        
        await popup.fill("input#mail-edit-subject", message.subject)
        await popup.fill("textarea#mail-edit-body-text", message.body)
        
        # 添付ファイルを追加する
        if message.attachment:
            await popup.click("#mail-edit-footer-section input[type='button'][value='選択']")
            async with popup.expect_file_chooser() as file_chooser_info:
                await popup.click("label[for='ifiles']:has-text('クリックしてファイルを選択してください')")
                file_chooser = await file_chooser_info.value
                await file_chooser.set_files(message.attachment)
                await popup.click("#jco-attachdlg + div button:has-text('OK')")
            
        # 送信を実行
        popup_toolbar = popup.locator("#toolbar")
        await popup_toolbar.get_by_role("button", name="送信").click()
        #-- 確認ダイアログの表示を待って、OKボタンをクリック
        await popup.wait_for_selector('.dialog-type-confirm', state='visible')
        await popup.locator(".dialog-type-confirm button.dialog-ok").click()
        
        # メインページに戻ったことを確認
        await self.page.wait_for_load_state('networkidle')
        
    def _ignore_error(self, func):
        """エラーを無視して関数を実行するデコレータ"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"Error ignored: {e}")
