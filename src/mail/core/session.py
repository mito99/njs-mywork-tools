import asyncio
from playwright.async_api import Page

from mail.core.exceptions import SessionError
from settings import DenbunSetting, Settings


class SessionManager:
    def __init__(self, page: Page, setting: DenbunSetting):
        self.page = page
        self._logged_in = False
        self._last_activity = None
        self.setting = setting

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in

    async def ensure_logged_in(self):
        """ログイン状態を確認し、必要に応じて再ログインを行う"""
        try:
            # ログイン状態チェック（例：特定の要素の有無で判断）
            is_logged_in = await self._check_login_status()
            if not is_logged_in:
                await self.login()
        except Exception as e:
            raise SessionError(f"ログイン状態の確認に失敗: {str(e)}")

    async def login(self):
        """ログイン処理を実行"""
        try:
            # ログインページに移動
            await self.page.goto(self.setting.url)
            
            # ログインフォームの入力
            await self.page.fill('input[name="UserID"]', self.setting.username)
            await self.page.fill('input[name="_word"]', self.setting.password)
            
            # ログインボタンクリック
            await self.page.get_by_role("button", name="ログイン").click()
            
            # ログイン成功の確認
            await self.page.wait_for_selector(
                'body[data-page=MailList]', 
                timeout=10000
            )
            
            self._logged_in = True
            self._last_activity = asyncio.get_running_loop().time()
        except Exception as e:
            raise SessionError(f"ログインに失敗: {str(e)}")

    async def _check_login_status(self) -> bool:
        """ログイン状態をチェック"""
        try:
            # セッション有効性の確認（例：特定の要素の存在確認）
            dashboard = await self.page.query_selector('.dashboard')
            return dashboard is not None
        except Exception:
            return False

    async def refresh_session(self):
        """セッションの更新が必要な場合に実行"""
        current_time = asyncio.get_event_loop().time()
        if (current_time - self._last_activity) > self.setting.session_timeout:
            await self.login()