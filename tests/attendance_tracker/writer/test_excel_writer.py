"""
ExcelWriterのテストモジュール
"""

from pathlib import Path

import pandas as pd
import pytest

from attendance_tracker.writer.excel_writer import ExcelWriter


class TestExcelWriter:
    """
    ExcelWriterのテストクラス
    """

    @pytest.fixture
    def sample_data(self):
        """
        テスト用のDataFrameを作成する
        """
        return pd.DataFrame(
            {
                "日付": ["2023-10-01", "2023-10-02"],
                "出勤時刻": ["09:00", "09:30"],
                "退勤時刻": ["17:30", "18:00"],
                "実労働時間": [7.5, 7.5],
            }
        )

    @pytest.fixture
    def template_path(self, tmp_path):
        """
        テスト用のテンプレートファイルを作成する
        """
        file_path = tmp_path / "template.xlsx"
        pd.DataFrame().to_excel(file_path, index=False)
        return file_path

    def test_write_success(self, sample_data, template_path, tmp_path):
        """
        正常系: Excelファイルの出力が成功することを確認
        """
        output_path = tmp_path / "output.xlsx"
        writer = ExcelWriter(template_path)
        writer.write(sample_data, output_path)

        # 出力されたファイルが存在することを確認
        assert output_path.exists()

        # 出力されたファイルの内容を確認
        df = pd.read_excel(output_path)
        assert len(df) == 2
        assert list(df.columns) == ["日付", "出勤時刻", "退勤時刻", "実労働時間"]

    def test_write_invalid_path(self, sample_data):
        """
        異常系: 不正なパスを指定した場合にエラーとなることを確認
        """
        writer = ExcelWriter(Path("not_exists.xlsx"))
        with pytest.raises(RuntimeError):
            writer.write(sample_data)
