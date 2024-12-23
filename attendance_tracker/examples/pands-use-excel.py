import pandas as pd
from pathlib import Path
from datetime import datetime

# Excelファイルのパスを指定
excel_path = Path(__file__).parent.parent / 'tests' / 'data' / 'input.xlsx'

try:
    # Scheduleシートを指定して読み込む
    df = pd.read_excel(excel_path, sheet_name='Timecard')
    
    # A列の名前を確認し、適切な列名に置き換えてください
    date_column = '日付'  # もしくは実際の列名（例：'date', 'scheduled_date'など）
    
    # 日付範囲を指定
    start_date = pd.to_datetime('2024-11-21')
    end_date = pd.to_datetime('2024-12-20')
    
    # 日付でフィルタリング
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    filtered_df = df.loc[mask]
    
    for index, row in filtered_df.iterrows():
        date = row["日付"]
        weekday = ['月', '火', '水', '木', '金', '土', '日'][date.dayofweek]
        holiday = True if pd.notna(row['祝日']) and row['祝日'] else False
        wk_type = row['種別']
        start_time = row['出社時間']
        end_time = row['退社時間']
        print(f"日付: {date}, 曜日: {weekday}, 祝日: {holiday}, 勤務種別: {wk_type}, 出社時間: {start_time}, 退社時間: {end_time}")

except FileNotFoundError:
    print(f"エラー: ファイル {excel_path} が見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
