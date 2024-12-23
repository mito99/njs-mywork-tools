"""
Excelファイルからデータを読み込むモジュール
"""

from pathlib import Path

import pandas as pd

from .. import settings


class ExcelReader:
    """
    Excelファイルから勤怠データを読み込むクラス
    """

    def __init__(self, file_path: Path):
        """
        初期化

        Args:
            file_path: 読み込むExcelファイルのパス
        """
        self.file_path = file_path

    def read(self) -> pd.DataFrame:
        """
        Excelファイルを読み込んでDataFrameとして返す

        Returns:
            pd.DataFrame: 読み込んだデータ
        """
        try:
            df = pd.read_excel(
                self.file_path,
                sheet_name=settings.SHEET_NAME,
                parse_dates=[settings.DATE_COL],
            )
            return df

        except Exception as e:
            raise RuntimeError(f"Excelファイルの読み込みに失敗しました: {str(e)}")
