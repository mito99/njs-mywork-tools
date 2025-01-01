#!/usr/bin/env python
"""
勤怠データ転記スクリプト

入力用Excelファイルから勤怠データを読み込み、出力用Excelファイルに転記します。
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from attendance.reader.excel_reader import ExcelReader
from attendance.writer.excel_writer import ExcelWriter


def parse_date(date_str: str) -> datetime:
    """日付文字列をdatetimeオブジェクトに変換する"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"日付の形式が不正です: {date_str} (YYYY-MM-DD形式で指定してください)")


def invoke(
    input_file: str | Path,
    output_file: str | Path,
    month: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> None:
    """
    勤怠データの転記処理を実行する

    Args:
        input_file (str | Path): 入力用Excelファイルのパス
        output_file (str | Path): 出力用Excelファイルのパス
        month (Optional[int], optional): 対象月 (1-12). Defaults to None.
        start_date (Optional[str], optional): 開始日 (YYYY-MM-DD形式). Defaults to None.
        end_date (Optional[str], optional): 終了日 (YYYY-MM-DD形式). Defaults to None.

    Raises:
        FileNotFoundError: 入力ファイルまたは出力ファイルが存在しない場合
        ValueError: 月の指定が不正な場合
    """
    # パスの検証
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")
    if not output_path.exists():
        raise FileNotFoundError(f"出力ファイルが見つかりません: {output_path}")

    # 日付の変換
    start_datetime = parse_date(start_date) if start_date else None
    end_datetime = parse_date(end_date) if end_date else None

    # 月の検証
    if month and not (1 <= month <= 12):
        raise ValueError(f"月の指定が不正です: {month} (1-12の範囲で指定してください)")

    # データの読み込みと書き込み
    try:
        reader = ExcelReader(input_path)
        writer = ExcelWriter(output_path)

        time_cards = reader.read_timecard_sheet(start_datetime, end_datetime)
        writer.write(month or datetime.now().month, time_cards)

        print("勤怠データの転記が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise


def main():
    """コマンドライン引数をパースしてinvoke関数を実行する"""
    parser = argparse.ArgumentParser(description='勤怠データを転記します')
    parser.add_argument('input_file', type=str, help='入力用Excelファイルのパス')
    parser.add_argument('output_file', type=str, help='出力用Excelファイルのパス')
    parser.add_argument('-m', '--month', type=int, help='対象月 (1-12)')
    parser.add_argument('-s', '--start_date', type=str, help='開始日 (YYYY-MM-DD形式)')
    parser.add_argument('-e', '--end_date', type=str, help='終了日 (YYYY-MM-DD形式)')

    args = parser.parse_args()

    invoke(
        input_file=args.input_file,
        output_file=args.output_file,
        month=args.month,
        start_date=args.start_date,
        end_date=args.end_date
    )


if __name__ == '__main__':
    main()
    # invoke(
    #     input_file='tests/attendance_tracker/data/input.xlsx',
    #     output_file='tests/attendance_tracker/data/output.xlsx',
    #     month=12,
    #     start_date='2024-11-21',
    #     end_date='2024-12-20'
    # )
