"""
ExcelReaderのテストモジュール
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from attendance.reader.excel_timecard_reader import ExcelTimeCardReader


class TestExcelTimeCardReader:
    """
    ExcelReaderのテストクラス
    """

    @pytest.fixture
    def actual_excel_path(self, tmp_path):
        """
        実際のExcelファイルを一時ディレクトリにコピーする
        """
        source_path = Path("tests/attendance_tracker/data/input.xlsx")
        dest_path = tmp_path / "input.xlsx"
        dest_path.write_bytes(source_path.read_bytes())
        return dest_path

    def test_read_actual_file(self, actual_excel_path):
        """
        正常系: 実際のExcelファイルの読み込みが成功することを確認
        """
        reader = ExcelTimecardReader(actual_excel_path)
        time_cards = reader.read_timecard_sheet(
            start_date=datetime(2024, 11, 21),
            end_date=datetime(2024, 12, 20),
        )

        assert len(time_cards) == 30

    def test_read_file_not_found(self):
        """
        異常系: 存在しないファイルを指定した場合にエラーとなることを確認
        """
        reader = ExcelTimecardReader(Path("not_exists.xlsx"))
        with pytest.raises(RuntimeError):
            reader.read()
