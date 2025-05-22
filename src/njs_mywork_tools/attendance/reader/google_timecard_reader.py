"""
Google Sheetsからデータを読み込むモジュール
"""

from datetime import date, datetime
from typing import List

import httplib2
import pandas as pd
from google.oauth2.service_account import Credentials
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build

from njs_mywork_tools.attendance.models.timecard_data import (TimeCardData,
                                                              TimeCardDataList)
from njs_mywork_tools.attendance.reader.timecard_reader import TimeCardReader
from njs_mywork_tools.settings import Settings


class GoogleTimeCardReader(TimeCardReader):
    """
    Google Sheetsから勤怠データを読み込むクラス
    """

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(
        self,
        credentials_path: str,
        spreadsheet_key: str,
        ssl_certificate_validation: bool = True,
    ):
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
            if ssl_certificate_validation:
                self.service = build("sheets", "v4", credentials=credentials)
            else:
                http = httplib2.Http(disable_ssl_certificate_validation=True)
                authorized_http = AuthorizedHttp(credentials, http=http)
                self.service = build("sheets", "v4", http=authorized_http)

            self.spreadsheet_key = spreadsheet_key

        except Exception as e:
            raise ValueError(f"Google Sheetsの認証に失敗しました: {str(e)}")

    def read_timecard_sheet(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> TimeCardDataList:
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
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_key, range="Timecard!A2:F")
                .execute()
            )
            values = result.get("values", [])

            time_cards = []
            for row in values:
                date = datetime.strptime(row[0].split(" ")[0], "%Y/%m/%d").date()
                if start_date and date < start_date:
                    continue
                if end_date and date > end_date:
                    break

                holiday = row[1].strip() != "" if len(row) > 1 else False
                work_type = row[2] if len(row) > 2 else ""
                time_in = (
                    datetime.strptime(row[3], "%H:%M").time() if len(row) > 3 else None
                )
                time_out = (
                    datetime.strptime(row[4], "%H:%M").time() if len(row) > 4 else None
                )

                work_time = (
                    datetime.strptime(row[5], "%H:%M").time() if len(row) > 5 else None
                )

                time_cards.append(
                    TimeCardData(
                        date=date,
                        holiday=holiday,
                        work_type=work_type,
                        time_in=time_in,
                        time_out=time_out,
                        work_time=work_time,
                    )
                )

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


if __name__ == "__main__":
    settings = Settings()
    reader = GoogleTimeCardReader(
        credentials_path=settings.google_sheet.credentials_path,
        spreadsheet_key=settings.google_sheet.spreadsheet_key,
        ssl_certificate_validation=settings.google_sheet.ssl_certificate_validation,
    )
    time_card_data_list = reader.read_timecard_sheet(
        start_date=datetime(2024, 12, 21).date(), end_date=datetime(2024, 12, 31).date()
    )
    print(time_card_data_list)
