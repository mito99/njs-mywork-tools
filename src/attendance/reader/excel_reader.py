"""
Excelファイルからデータを読み込むモジュール
"""

from pathlib import Path
from typing import List
from datetime import datetime

import pandas as pd

from attendance.models.timecard_data import TimeCardData, TimeCardDataList


class ExcelReader:
    """
    Excelファイルから勤怠データを読み込むクラス
    """

    def __init__(self, file_path: str | Path):
        """
        初期化

        Args:
            file_path: 読み込むExcelファイルのパス
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    def read_timecard_sheet(self, start_date: datetime | None = None, end_date: datetime | None = None) -> TimeCardDataList:
        """
        Excelファイルから出退勤データを読み込む

        Parameters
        ----------
        start_date : datetime | None, optional
            読み込み開始日, by default None
        end_date : datetime | None, optional
            読み込み終了日, by default None

        Returns
        -------
        List[TimeCardData]
            読み込んだ出退勤データ
        """
        try:
            df = pd.read_excel(
                self.file_path,
                sheet_name='Timecard',
                parse_dates=['日付', '祝日', '種別', '出社時間', '退社時間']
            )

            # 日付でフィルタリング
            if start_date is not None:
                df = df[df['日付'] >= pd.to_datetime(start_date)]
            if end_date is not None:
                df = df[df['日付'] <= pd.to_datetime(end_date)]
            
            time_cards = []
            for _, row in df.iterrows():
                time_cards.append(TimeCardData(
                    date=row['日付'],
                    holiday=row['祝日'],
                    work_type=row['種別'],
                    time_in=row['出社時間'] if pd.notna(row['出社時間']) else None,
                    time_out=row['退社時間'] if pd.notna(row['退社時間']) else None,
                ))
                
            return TimeCardDataList(time_cards)
            
        except Exception as e:
            raise ValueError(f"Excelファイルの読み込みに失敗しました: {str(e)}")

    def get_sheet_names(self) -> List[str]:
        """
        Excelファイルのシート名一覧を取得する

        Returns
        -------
        List[str]
            シート名のリスト
        """
        try:
            return pd.ExcelFile(self.file_path).sheet_names
        except Exception as e:
            raise ValueError(f"シート名の取得に失敗しました: {str(e)}")
