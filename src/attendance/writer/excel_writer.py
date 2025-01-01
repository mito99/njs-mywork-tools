"""
処理結果をExcelファイルに出力するモジュール
"""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import tempfile
from typing import List, Generator

import xlwings as xw

import pandas as pd

from attendance.models.timecard_data import TimeCardData, TimeCardDataList
from utils.shokuin import create_shokuin

from .. import settings


def _to_int(value: str, default: int = 0) -> int:
    """
    文字列を整数に変換する。変換に失敗した場合はデフォルト値を返却する。

    Args:
        value (str): 変換対象の文字列
        default (int): デフォルト値。デフォルトは0

    Returns:
        int: 変換後の整数値
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class ExcelWriter:
    """
    処理結果をExcelファイルに出力するクラス
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def _stamp_syokuin(self, sheet: xw.Sheet, cell:str, text1:str, text2:str, text3:str) -> None:
        """
        出勤印を押す
        """
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            syokuin_image = create_shokuin(text1, text2, text3, size=300)
            syokuin_image.save(tmp.name)

            for pic in sheet.pictures:
                if pic.name == 'syokuin':
                    pic.delete()
            
            sheet.pictures.add(
                tmp.name,
                left=sheet.range(cell).left - 5,
                top=sheet.range(cell).top - 5,
                width=70,
                height=70,
                name='syokuin'
            )

    def write(self, month: int, time_cards: TimeCardDataList) -> None:
        """
        処理結果をExcelファイルに出力する
        """
        date_dict = time_cards.to_date_dict()
        
        with self._open_book() as wb:
            sheet = wb.sheets[f"{month}月"]
            sheet.activate()
            
            # 職印を押す
            today = datetime.now().strftime('%Y.%m.%d')
            self._stamp_syokuin(sheet, 'S4', '山田', today, '太郎')

            # データ行を処理する
            for col in range(10, 41):
                # 月が数字でない場合はデータ行は終わりと判定
                cell_month = _to_int(sheet.range(f'C{col}').value, default=None)
                if cell_month is None:
                    print(f"データ行が終わりました: {col}")
                    break
                
                cell_day = _to_int(sheet.range(f'D{col}').value, default=None)
                if cell_day is None:
                    print(f"データ行が終わりました: {col}")
                    break
                
                data = date_dict.get(f"{cell_month}_{cell_day}")
                
                if data:
                    sheet.range(f'F{col}').value = data.work_type_str()
                    sheet.range(f'L{col}').value = data.time_in_str()
                    sheet.range(f'M{col}').value = data.time_out_str()

            wb.save()

    @contextmanager
    def _open_book(self) -> Generator[xw.Book, None, None]:
        """
        Excelファイルを開く
        """
        with xw.App(visible=True, add_book=False) as app:
            with app.books.open(self.file_path) as wb:
                yield wb
