# Pythonコード
import dotenv
from google.oauth2.credentials import Credentials
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

dotenv.load_dotenv()

# スコープの設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE=os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE_PATH')

def get_timesheet_data():
    # 認証情報の設定
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    
    # Sheets APIのサービス構築
    service = build('sheets', 'v4', credentials=credentials)

    # スプレッドシートIDとレンジの指定
    SPREADSHEET_ID = '1d-ja9DnY2NhO_i3Je3Z9lb3bLr3tsR00ImnafWCjsJQ'
    RANGE_NAME = 'Timecard!A2:F'

    # データの取得
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    
    values = result.get('values', [])
    return values

# 使用例
timesheet_data = get_timesheet_data()
for row in timesheet_data:
    date, start_time, end_time = row
    print(f'日付: {date}, 開始: {start_time}, 終了: {end_time}')


if __name__ == '__main__':
    get_timesheet_data()
