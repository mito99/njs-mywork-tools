"""
Google Sheetsからデータを読み込むモジュール
"""

from datetime import datetime
from typing import List
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from attendance.models.timecard_data import TimeCardData, TimeCardDataList
from settings import Settings


class GoogleSheetReader:
    """
    Google Sheetsから勤怠データを読み込むクラス
    """

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(self, credentials_path: str, spreadsheet_key: str):
        """
        初期化

        Args:
            credentials_path: サービスアカウントの認証情報JSONファイルのパス
            spreadsheet_key: 読み込むスプレッドシートのキー
        """
        try:
            credentials = Credentials.from_service_account_file(
                credentials_path, scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.spreadsheet_key = spreadsheet_key

        except Exception as e:
            raise ValueError(f"Google Sheetsの認証に失敗しました: {str(e)}")

    def read_timecard_sheet(self, start_date: datetime | None = None, end_date: datetime | None = None) -> TimeCardDataList:
        """
        Google Sheetsから出退勤データを読み込む

        Parameters
        ----------
        start_date : datetime | None, optional
            読み込み開始日, by default None
        end_date : datetime | None, optional
            読み込み終了日, by default None

        Returns
        -------
        TimeCardDataList
            読み込んだ出退勤データ
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_key,
                range='Timecard!A2:F'
            ).execute()
            values = result.get('values', [])
            
            time_cards = []
            for row in values:
                date = datetime.strptime(row[0].split(' ')[0], '%Y/%m/%d').date()
                holiday = (row[1] if len(row) > 1 else '').strip() != ''
                work_type = row[2] if len(row) > 2 else ''
                time_in = datetime.strptime(row[3], '%H:%M').time() if len(row) > 3 else None
                time_out = datetime.strptime(row[4], '%H:%M').time() if len(row) > 4 else None

                time_cards.append(TimeCardData(
                    date=date,
                    holiday=holiday,
                    work_type=work_type,
                    time_in=time_in,
                    time_out=time_out
                ))

            return TimeCardDataList(time_cards)

        except Exception as e:
            raise ValueError(f"Google Sheetsの読み込みに失敗しました: {str(e)}")

    def get_sheet_names(self) -> List[str]:
        """
        スプレッドシートのシート名一覧を取得する

        Returns
        -------
        List[str]
            シート名のリスト
        """
        try:
            return [worksheet.title for worksheet in self.spreadsheet.worksheets()]
        except Exception as e:
            raise ValueError(f"シート名の取得に失敗しました: {str(e)}")

if __name__ == '__main__':
    settings = Settings()
    reader = GoogleSheetReader(
        credentials_path=settings.google_sheet.credentials_path,
        spreadsheet_key=settings.google_sheet.spreadsheet_key
    )
    reader.read_timecard_sheet()
