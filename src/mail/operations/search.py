import asyncio
from typing import AsyncIterator, List, Optional
from datetime import datetime, time, timedelta
from playwright.async_api import Page

from mail.core.exceptions import MailOperationError
from mail.models.message import MailMessage

class MailSearchOperation:
    """メール検索操作を行うクラス"""
    
    def __init__(self, page: Page):
        self.page = page

    async def search_messages(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        after_message_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[MailMessage]:
        """
        メールリストを検索して取得する

        Args:
            start_date: 検索開始日
            end_date: 検索終了日
            keyword: 検索キーワード
            after_message_id: この ID 以降のメッセージを取得

        Returns:
            List[MailMessage]: 検索結果のメールリスト
        
        Raises:
            MailOperationError: メール検索に失敗した場合
        """
        messages = []
        async for message in self.search_messages_iter(
            start_date=start_date,
            end_date=end_date,
            after_message_id=after_message_id,
            keyword=keyword
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
            keyword: 検索キーワード
            after_message_id: この ID 以降のメッセージを取得

        Yields:
            MailMessage: 検索結果のメール

        Raises:
            MailOperationError: メール検索に失敗した場合
        """
        try:
            # メール一覧の要素が表示されるまで待機
            await self.page.wait_for_selector('#mail-table [data-id^="INBOX_"]')
            
            # 最初のメールを選択
            first_element = self.page.locator('#mail-table [data-id^="INBOX_"]').first
            await first_element.click()
            await self.page.wait_for_timeout(1000)

            # 最初のメールの情報を取得
            first_message = await self._fetch_message_info()
            if not after_message_id or first_message.id > after_message_id:
                if (not start_date or first_message.received_at >= start_date) and \
                   (not end_date or first_message.received_at <= end_date):
                    yield first_message

            # 次のメールを取得し続ける
            while await self._move_to_next_message(after_message_id):
                message = await self._fetch_message_info()
                
                # 時系列順に並んでる前提
                if end_date and message.received_at > end_date:
                    break
                if start_date and message.received_at < start_date:
                    break
                    
                yield message
                
        except Exception as e:
            raise MailOperationError(f"メール検索に失敗しました: {str(e)}") 

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
        from_address = await self.page.locator(".mail-view-header-from a[data-value]").nth(1).get_attribute("data-value")
        to_elements = await self.page.locator(".mail-view-header-to a[data-value]").all()
        to_addresses = [await el.get_attribute("data-value") for el in to_elements]
        
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
            received_at=received_at,
            body=body or "",
            sender=from_address or "",
            recipients=to_addresses,
            attachments=attachments
        )

    async def _move_to_next_message(self, after_message_id: Optional[str] = None) -> bool:
        """次のメッセージに移動する"""
        for _ in range(2):
            selected_row = self.page.locator("tr.com_table-row-selected") 
            selected_id = await selected_row.get_attribute("data-id")
            
            next_row = self.page.locator(f"tr[data-id='{selected_id}'] + tr[data-id^='INBOX_']")
            if not await next_row.is_visible():
                await self.page.mouse.wheel(0, 100000)
                await asyncio.sleep(1)
                continue
            
            await next_row.click()
            await self.page.wait_for_timeout(1000)
            
            clicked_row = self.page.locator("tr.com_table-row-selected")
            clicked_id = await clicked_row.get_attribute("data-id")

            return clicked_id != selected_id

