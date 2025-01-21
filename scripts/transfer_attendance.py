#!/usr/bin/env python
"""
勤怠データ転記スクリプト

入力用Excelファイルから勤怠データを読み込み、出力用Excelファイルに転記します。
"""

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from venv import create

from njs_mywork_tools.attendance.models.employee import Employee
from njs_mywork_tools.attendance.reader.excel_timecard_reader import \
    ExcelTimeCardReader
from njs_mywork_tools.attendance.reader.google_timecard_reader import \
    GoogleTimeCardReader
from njs_mywork_tools.attendance.reader.timecard_reader import TimeCardReader
from njs_mywork_tools.attendance.writer.excel_writer import ExcelWriter
from njs_mywork_tools.settings import Settings

settings = Settings()


def parse_date(date_str: str) -> date:
    """日付文字列をdateオブジェクトに変換する"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"日付の形式が不正です: {date_str} (YYYY-MM-DD形式で指定してください)"
        )


def create_time_card_reader(source: str | Path):
    if source == "google":
        time_card_reader = GoogleTimeCardReader(
            credentials_path=settings.google_sheet.credentials_path,
            spreadsheet_key=settings.google_sheet.spreadsheet_key,
            ssl_certificate_validation=settings.google_sheet.ssl_certificate_validation,
        )
        return time_card_reader
    return ExcelTimeCardReader(file_path=source)


def invoke(
    source: str | Path,
    template_file: str | Path,
    output_file: str | Path,
    name: str,
    month: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    勤怠データの転記処理を実行する

    Args:
        source: (str | Path): タイムカードソース("google" or Excelファイルパス)
        template_file (str | Path): テンプレートExcelファイルのパス
        output_file (str | Path): 出力用Excelファイルのパス
        name (str): 氏名
        month (Optional[int], optional): 対象月 (1-12). Defaults to None.
        start_date (Optional[str], optional): 開始日 (YYYY-MM-DD形式). Defaults to None.
        end_date (Optional[str], optional): 終了日 (YYYY-MM-DD形式). Defaults to None.

    Raises:
        FileNotFoundError: 入力ファイルまたは出力ファイルが存在しない場合
        ValueError: 月の指定が不正な場合
    """
    # パスの検証
    output_path = Path(output_file)
    if not output_path.parent.exists():
        raise FileNotFoundError(f"出力先ディレクトリが存在しません: {output_path.parent}")
    
    template_path = Path(template_file)    
    if not template_path.exists():
        raise FileNotFoundError(f"テンプレートファイルが見つかりません: {template_path}")

    # 日付の変換
    start_date_obj = parse_date(start_date) if start_date else None
    end_date_obj = parse_date(end_date) if end_date else None

    # 月の検証
    if month and not (1 <= month <= 12):
        raise ValueError(f"月の指定が不正です: {month} (1-12の範囲で指定してください)")

    # データの読み込みと書き込み
    try:
        employee = Employee.from_full_name(name)
        reader = create_time_card_reader(source)
        writer = ExcelWriter(template_path, employee)

        time_cards = reader.read_timecard_sheet(start_date_obj, end_date_obj)
        writer.write_to_file(output_path, month or datetime.now().month, time_cards)

        print("勤怠データの転記が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise


def main():
    """コマンドライン引数をパースしてinvoke関数を実行する"""
    parser = argparse.ArgumentParser(description="勤怠データを転記します")
    parser.add_argument("output_file", type=str, help="出力用Excelファイルのパス")
    parser.add_argument("template_file", type=str, help="テンプレートExcelファイルのパス")
    parser.add_argument("-n", "--name", type=str, help="氏名 (例:山田 太郎)")
    parser.add_argument("-m", "--month", type=int, help="対象月 (1-12)")
    parser.add_argument("-s", "--start_date", type=str, help="開始日 (YYYY-MM-DD形式)")
    parser.add_argument("-e", "--end_date", type=str, help="終了日 (YYYY-MM-DD形式)")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="データの読み込み元を指定します。ローカルのExcelファイルのパスまたは 'google' を指定します",
    )

    args = parser.parse_args()

    invoke(
        source=args.source,
        template_file=args.template_file,
        output_file=args.output_file,
        name=args.name,
        month=args.month,
        start_date=args.start_date,
        end_date=args.end_date,
    )


if __name__ == "__main__":
    # main()
    invoke(
        source="google",
        output_file="tmp/output.xlsx",
        template_file="tests/data/template.xlsx",
        month=1,
        start_date="2024-12-21",
        end_date="2025-01-20",
        name="山田 太郎",
    )
