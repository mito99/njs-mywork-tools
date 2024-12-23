"""
勤怠管理ツールのメインエントリーポイント
"""

import logging
from pathlib import Path

from settings import Settings


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


settings = Settings()

def main():
    """
    メイン処理を実行
    """
    
    print(settings)


if __name__ == "__main__":
    main()
