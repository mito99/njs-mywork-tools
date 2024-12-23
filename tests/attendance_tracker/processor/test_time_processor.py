"""
TimeProcessorのテストモジュール
"""

from datetime import datetime
from pathlib import Path
import shutil

import pandas as pd
import pytest

from attendance_tracker.reader.excel_reader import ExcelReader


class TestExcelReader:
    """
    ExcelReaderのテストクラス
    """

    @pytest.fixture
    def sample_excel_path(tmp_path):
        """
        tests/data/input.xlsx をテスト用のファイルとしてコピーして使用する

        Returns
        -------
        Path
            テスト用Excelファイルのパス
        """
        # テストデータファイルのパスを取得
        test_data_path = Path(__file__).parent.parent / "data" / "input.xlsx"
        
        # 一時ディレクトリにコピー
        dest_path = tmp_path / "input.xlsx"
        shutil.copy2(test_data_path, dest_path)
        
        return dest_path

    def test_init_file_not_found(self):
        """
        異常系: 存在しないファイルを指定した場合にFileNotFoundErrorが発生することを確認
        """
        with pytest.raises(FileNotFoundError):
            ExcelReader("not_exists.xlsx")

    def test_read_timecard_sheet_success(self, sample_excel_path):
        """
        正常系: タイムカードシートの読み込みが成功することを確認
        """
        reader = ExcelReader(sample_excel_path)
        time_cards = reader.read_timecard_sheet()

        assert len(time_cards) == 3
        first_record = time_cards[0]
        assert first_record.date == pd.Timestamp("2023-10-01")
        assert first_record.time_in == pd.Timestamp("2023-10-01 09:00:00")
        assert first_record.time_out == pd.Timestamp("2023-10-01 17:30:00")
        assert first_record.break_start == pd.Timestamp("2023-10-01 12:00:00")
        assert first_record.break_end == pd.Timestamp("2023-10-01 13:00:00")
        assert first_record.remarks == "通常勤務"

    def test_read_timecard_sheet_with_date_filter(self, sample_excel_path):
        """
        正常系: 日付でフィルタリングした読み込みが成功することを確認
        """
        reader = ExcelReader(sample_excel_path)
        start_date = datetime(2023, 10, 2)
        end_date = datetime(2023, 10, 2)
        
        time_cards = reader.read_timecard_sheet(start_date=start_date, end_date=end_date)
        
        assert len(time_cards) == 1
        assert time_cards[0].date == pd.Timestamp("2023-10-02")
        assert time_cards[0].remarks == "遅刻"

    def test_get_sheet_names(self, sample_excel_path):
        """
        正常系: シート名の取得が成功することを確認
        """
        reader = ExcelReader(sample_excel_path)
        sheet_names = reader.get_sheet_names()
        
        assert len(sheet_names) == 2
        assert "Timecard" in sheet_names
        assert "Settings" in sheet_names

    def test_read_invalid_excel(self, tmp_path):
        """
        異常系: 無効なExcelファイルを読み込もうとした場合にValueErrorが発生することを確認
        """
        invalid_file = tmp_path / "invalid.xlsx"
        invalid_file.write_text("This is not an Excel file")
        
        reader = ExcelReader(invalid_file)
        with pytest.raises(ValueError):
            reader.read_timecard_sheet()
