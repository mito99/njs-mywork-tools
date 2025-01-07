import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    max_bytes: int = 1024 * 1024,  # 1MB
    backup_count: int = 5
) -> logging.Logger:
    """アプリケーション用のロガーをセットアップする

    Args:
        name: ロガー名
        log_file: ログファイルパス
        level: ログレベル
        max_bytes: ログファイルの最大サイズ
        backup_count: 保持する過去ログファイル数

    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # フォーマッターの作成
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 標準出力へのハンドラー
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # ファイル出力の設定（指定がある場合）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger 