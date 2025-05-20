"""
処理結果をExcelファイルに出力するモジュール
"""

import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Generator, TypedDict

import xlwings as xw

from njs_mywork_tools.attendance.models.employee import Employee
from njs_mywork_tools.attendance.models.timecard_data import TimeCardDataList
from njs_mywork_tools.utils.shokuin import create_shokuin


class ConfigDict(TypedDict):
    xlwings_visible: bool

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

    def __init__(self, template_path: Path, employee: Employee, config: ConfigDict ={
        "xlwings_visible": False
    }):
        self.template_path = template_path
        self.employee = employee
        self.xlwings_visible = config.get("xlwings_visible", False)

    def _stamp_syokuin(
        self, sheet: xw.Sheet, cell: str, text1: str, text2: str, text3: str
    ) -> None:
        """
        出勤印を押す
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            syokuin_image = create_shokuin(text1, text2, text3, size=300)
            syokuin_image.save(tmp.name)

            for pic in sheet.pictures:
                if pic.name == "syokuin":
                    pic.delete()

            sheet.pictures.add(
                tmp.name,
                left=sheet.range(cell).left - 5,
                top=sheet.range(cell).top - 5,
                width=70,
                height=70,
                name="syokuin",
            )

    def write(self, output: BinaryIO, month: int, time_cards: TimeCardDataList) -> None:
        """
        タイムカードデータをExcelファイルに書き出す

        Args:
            output (BinaryIO): 出力先のファイルパス
            month (int): 対象月
            time_cards (TimeCardDataList): タイムカードデータ
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            self.write_to_file(tmp.name, month, time_cards)
            
            with open(tmp.name, "rb") as f:
                output.write(f.read())
            os.unlink(tmp.name)

    def write_to_file(self, output_path: Path, month: int, time_cards: TimeCardDataList) -> None:
        """
        タイムカードデータをExcelファイルに書き出す

        Args:
            output_path (Path): 出力先のファイルパス
            month (int): 対象月
            time_cards (TimeCardDataList): タイムカードデータ
        """
        date_dict = time_cards.to_date_dict()

        with self._open_book() as wb:
            sheet = wb.sheets[f"{month}月"]
            sheet.activate()

            # 職印を押す
            today = datetime.now().strftime("%Y.%m.%d")
            self._stamp_syokuin(sheet, "T4", "JS", today, self.employee.family_name)

            # データ行を処理する
            for col in range(10, 41):
                # 月が数字でない場合はデータ行は終わりと判定
                cell_month = _to_int(sheet.range(f"C{col}").value, default=None)
                if cell_month is None:
                    print(f"データ行が終わりました: {col}")
                    break

                cell_day = _to_int(sheet.range(f"D{col}").value, default=None)
                if cell_day is None:
                    print(f"データ行が終わりました: {col}")
                    break

                data = date_dict.get(f"{cell_month}_{cell_day}")

                if data:
                    sheet.range(f"F{col}").value = data.work_type_str()
                    sheet.range(f"L{col}").value = data.overtime_start_time_str()
                    sheet.range(f"M{col}").value = data.overtime_end_time_str()
                    sheet.range(f"V{col}").value = (
                        "1" if data.work_type == "出勤" else ""
                    )
                    sheet.range(f"W{col}").value = (
                        "1" if data.work_type == "在宅" else ""
                    )
                else:
                    sheet.range(f"F{col}").value = ""
                    sheet.range(f"L{col}").value = ""
                    sheet.range(f"M{col}").value = ""
                    sheet.range(f"V{col}").value = ""
                    sheet.range(f"W{col}").value = ""

            if output_path == self.template_path:
                wb.save()
            else:
                wb.save(output_path)

    @contextmanager
    def _open_book(self) -> Generator[xw.Book, None, None]:
        """
        Excelファイルを開く
        """
        with xw.App(visible=self.xlwings_visible, add_book=False) as app:
            with app.books.open(self.template_path) as wb:
                yield wb