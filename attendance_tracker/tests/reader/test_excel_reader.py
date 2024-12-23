"""
ExcelReaderのテストモジュール
"""

from pathlib import Path

import pandas as pd
import pytest

from attendance_tracker.src.reader.excel_reader import ExcelReader


class TestExcelReader:
    """
    ExcelReaderのテストクラス
    """

    @pytest.fixture
    def sample_excel_path(self, tmp_path):
        """
        テスト用のExcelファイルを作成する
        """
        file_path = tmp_path / "test_input.xlsx"
        df = pd.DataFrame(
            {
                "日付": ["2023-10-01", "2023-10-02"],
                "出勤時刻": ["09:00", "09:30"],
                "退勤時刻": ["17:30", "18:00"],
            }
        )
        df.to_excel(file_path, index=False)
        return file_path

    def test_read_success(self, sample_excel_path):
        """
        正常系: Excelファイルの読み込みが成功することを確認
        """
        reader = ExcelReader(sample_excel_path)
        df = reader.read()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["日付", "出勤時刻", "退勤���刻"]

    def test_read_file_not_found(self):
        """
        異常系: 存在しないファイルを指定した場合にエラーとなることを確認
        """
        reader = ExcelReader(Path("not_exists.xlsx"))
        with pytest.raises(RuntimeError):
            reader.read()
