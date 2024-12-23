"""
勤怠時間の処理を行うモジュール
"""

from datetime import datetime, timedelta

import pandas as pd

from .. import settings


class TimeProcessor:
    """
    勤怠時間の計算と処理を行うクラス
    """

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        勤怠データを処理する

        Args:
            df: 処理対象のDataFrame

        Returns:
            pd.DataFrame: 処理済みのDataFrame
        """
        try:
            # 時間計算のための一時的なDataFrameを作成
            result_df = df.copy()

            # 勤務時間の計算
            result_df["実労働時間"] = self._calculate_work_hours(
                result_df[settings.START_TIME_COL], result_df[settings.END_TIME_COL]
            )

            return result_df

        except Exception as e:
            raise RuntimeError(f"時間処理に失敗しました: {str(e)}")

    def _calculate_work_hours(
        self, start_times: pd.Series, end_times: pd.Series
    ) -> pd.Series:
        """
        実労働時間を計算する

        Args:
            start_times: 出勤時刻のSeries
            end_times: 退勤時刻のSeries

        Returns:
            pd.Series: 実労働時間（時間単位）
        """
        # 時間をdatetime型に変換
        start_times = pd.to_datetime(start_times)
        end_times = pd.to_datetime(end_times)

        # 勤務時間を計算（分単位）
        work_minutes = (end_times - start_times).dt.total_seconds() / 60

        # 休憩時間を考慮
        work_minutes = work_minutes - settings.BREAK_TIME

        # 時間単位に変換（小数点以下2桁まで）
        work_hours = (work_minutes / 60).round(2)

        return work_hours
