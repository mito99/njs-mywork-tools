class DeboonError(Exception):
    """Deboon関連の基本例外クラス"""
    pass

class SessionError(DeboonError):
    """セッション管理に関する例外"""
    pass

class AuthenticationError(SessionError):
    """認証失敗時の例外"""
    pass

class BrowserOperationError(DeboonError):
    """ブラウザ操作に関する例外"""
    pass

class MailOperationError(DeboonError):
    """メール操作に関する例外"""
    pass