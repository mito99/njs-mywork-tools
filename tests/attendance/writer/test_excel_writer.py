"""
ExcelWriterのテストモジュール
"""
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import xlwings as xw

from attendance.writer.excel_writer import ExcelWriter
from attendance.models.timecard_data import TimeCardData, TimeCardDataList


class TestExcelWriter:
    """
    ExcelWriterのテストクラス
    """

    @pytest.fixture
    def actual_excel_path(self, tmp_path):
        """
        実際のExcelファイルを一時ディレクトリにコピーする
        """
        source_path = Path("tests/attendance_tracker/data/output.xlsx")
        dest_path = tmp_path / "output.xlsx"
        dest_path.write_bytes(source_path.read_bytes())
        return dest_path
    
    def test_write(self, actual_excel_path):
        """
        正常系: 処理結果をExcelファイルに出力する
        """
        writer = ExcelWriter(actual_excel_path)
        time_cards = TimeCardDataList([
            TimeCardData(
                date=datetime(2024, 11, 21),
                holiday=False,
                work_type="在宅",
                time_in=datetime(2024, 11, 21, 8, 50),
                time_out=datetime(2024, 11, 21, 18, 40),
            ),
            TimeCardData(
                date=datetime(2024, 11, 22),
                holiday=False,
                work_type="有休",
                time_in=datetime(2024, 11, 22, 8, 50),
                time_out=datetime(2024, 11, 22, 18, 40),
            ),
        ])
        writer.write(12, time_cards)
