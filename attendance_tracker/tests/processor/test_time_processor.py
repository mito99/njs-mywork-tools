"""
TimeProcessorのテストモジュール
"""

import pandas as pd
import pytest

from attendance_tracker.src.processor.time_processor import TimeProcessor


class TestTimeProcessor:
    """
    TimeProcessorのテストクラス
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
            }
        )

    def test_process_success(self, sample_data):
        """
        正常系: 勤務時間の計算が正しく行われることを確認
        """
        processor = TimeProcessor()
        result = processor.process(sample_data)

        assert "実労働時間" in result.columns
        assert len(result) == 2

        # 1日目: 17:30 - 9:00 - 1:00(休憩) = 7.5時間
        assert result.iloc[0]["実労働時間"] == 7.5

        # 2日目: 18:00 - 9:30 - 1:00(休憩) = 7.5時間
        assert result.iloc[1]["実労働時間"] == 7.5

    def test_process_invalid_time(self):
        """
        異常系: 不正な時刻データの場合にエラーとなることを確認
        """
        invalid_data = pd.DataFrame(
            {"日付": ["2023-10-01"], "出勤時刻": ["invalid"], "退勤時刻": ["17:30"]}
        )

        processor = TimeProcessor()
        with pytest.raises(RuntimeError):
            processor.process(invalid_data)
