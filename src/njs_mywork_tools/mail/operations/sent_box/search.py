import asyncio
from datetime import datetime
from typing import AsyncIterator, List, Optional

from playwright.async_api import Page

from njs_mywork_tools.mail.core.exceptions import MailOperationError
from njs_mywork_tools.mail.models.message import ContactPerson, MailMessage


class SentBoxSearchOperation:
    """送信ボックスのメール検索操作を行うクラス"""
    
    def __init__(self, page: Page):
        self.page = page

    async def search_messages(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> List[MailMessage]:
        """
        メールリストを検索して取得する

        Args:
            start_date: 検索開始日
            end_date: 検索終了日
            keyword: 検索キーワード
    
        Returns:
            List[MailMessage]: 検索結果のメールリスト
        """
        messages = []
        async for message in self.search_messages_iter(
            start_date=start_date, end_date=end_date, keyword=keyword
        ):
            messages.append(message)
        return messages

    async def search_messages_iter(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        after_message_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> AsyncIterator[MailMessage]:
        """
        メールリストを検索して順次取得する

        Args:
            start_date: 検索開始日
            end_date: 検索終了日
            after_message_id: この ID 以降のメッセージを取得
            keyword: 検索キーワード
        """
    
        try:
            mail_folder = self.page.locator("#mail-folder")
            await mail_folder.locator('span:text("送信ボックス")').click()
            
            await self.page.wait_for_selector("#mail-table [data-id^='Sent_']")
            
            first_element = self.page.locator("#mail-table [data-id^='Sent_']").first
            await first_element.click()
            await self.page.wait_for_timeout(1000)
            
            first_message = await self._fetch_message_info()
            if not after_message_id or first_message.id > after_message_id:
                if (not start_date or first_message.mail_date >= start_date) and \
                (not end_date or first_message.mail_date <= end_date):
                    yield first_message

            while await self._move_to_next_message(after_message_id):
                message = await self._fetch_message_info()

                if end_date and message.mail_date > end_date:
                    continue
                if start_date and message.mail_date < start_date:
                    break
                yield message
        except Exception as e:
            raise MailOperationError(f"メール検索に失敗しました: {str(e)}")

    async def _move_to_next_message(self, after_message_id: Optional[str]) -> bool:
        """次のメッセージに移動する"""
        for _ in range(2):
            selected_row = self.page.locator("tr.com_table-row-selected") 
            selected_id = await selected_row.get_attribute("data-id")
            
            next_row = self.page.locator(f"tr[data-id='{selected_id}'] + tr[data-id^='Sent_']")
            if not await next_row.is_visible():
                await self.page.mouse.wheel(0, 100000)
                await asyncio.sleep(1)
                continue
            
            await next_row.click()
            await self.page.wait_for_timeout(1000)
            
            clicked_row = self.page.locator("tr.com_table-row-selected")
            clicked_id = await clicked_row.get_attribute("data-id")

            return clicked_id != selected_id 

    async def _fetch_message_info(self) -> MailMessage:
        """メール詳細情報を取得する"""
        await self.page.wait_for_selector("iframe#mail-view-body-frame", state="attached")

        # 現在選択されている行からIDを取得
        row = self.page.locator("tr.com_table-row-selected")
        message_id = await row.get_attribute("data-id")

        # iframe内のメール本文を取得
        iframe = await self.page.query_selector("iframe#mail-view-body-frame")
        frame = await iframe.content_frame()
        body = await frame.text_content("body")

        # メールヘッダー情報を取得
        from_address = await self.page.locator(
            ".mail-view-header-from a[data-value]").nth(1).get_attribute("data-value")        
        sender = ContactPerson.from_email_format(from_address)
        
        to_elements = await self.page.locator(".mail-view-header-to a[data-value]").all()
        to_addresses = [
            ContactPerson.from_email_format(await el.get_attribute("data-value")) 
            for el in to_elements
        ]
        
        cc_elements = await self.page.locator(".mail-view-header-cc a[data-value]").all()
        cc_addresses = [
            ContactPerson.from_email_format(await el.get_attribute("data-value")) 
            for el in cc_elements
        ]
        
        receive_date = await self.page.locator(".mail-view-header-datetime").nth(1).text_content()
        subject = await self.page.locator("#mail-view-subject").text_content()
        
        # 添付ファイル名の取得
        attachments = []
        attachment_button = self.page.locator("#mail-view-header-show_attachment")
        if await attachment_button.is_visible():
            await attachment_button.click()
            
        attachment_list = self.page.locator("#mail-view-header-attachment-list")
        if await attachment_list.is_visible():
            attachments = await attachment_list.all_text_contents()

        received_at = datetime.strptime(receive_date, '%Y/%m/%d %H:%M')

        return MailMessage(
            id=message_id,
            subject=subject or "",
            mail_date=received_at,
            body=body or "",
            sender=sender,
            to_addresses=to_addresses,
            cc_addresses=cc_addresses,
            attachments=attachments
        )

