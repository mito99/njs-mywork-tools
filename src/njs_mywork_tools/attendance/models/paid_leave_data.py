from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List


class PaidLeaveType(Enum):
    """
    有給休暇の種類
    """
    FULL_DAY = "全日休"  # 全日休
    MORNING = "午前休"   # 午前休
    AFTERNOON = "午後休"  # 午後休

    @classmethod
    def from_work_type(cls, work_type: str) -> 'PaidLeaveType':
        """
        勤務タイプから有給休暇の種類を判定するファクトリメソッド

        Args:
            work_type (str): 勤務タイプを表す文字列

        Returns:
            PaidLeaveType: 対応する有給休暇の種類
        """
        if work_type in ('有休', '有給'):
            return cls.FULL_DAY
        
        if work_type in ("午前休/在宅", "午前休/出勤"):
            return cls.MORNING
        
        if work_type in ("在宅/午後休", "出勤/午後休"):
            return cls.AFTERNOON
        
        raise ValueError(f"無効な勤務タイプです: {work_type}")

    @classmethod
    def is_valid_work_type(cls, work_type: str) -> bool:
        """
        与えられた勤務タイプが有給休暇の種類として有効かどうかを判定する

        Args:
            work_type (str): 勤務タイプを表す文字列

        Returns:
            bool: 有効な勤務タイプの場合はTrue、そうでない場合はFalse
        """
        try:
            cls.from_work_type(work_type)
            return True
        except ValueError:
            return False

@dataclass
class PaidLeaveData:
    """
    有給管理データ
    """
    
    application_date: date  # 有給休暇の申請日
    leave_type: PaidLeaveType  # 有給休暇の種類
    stamp_exists: bool = False  # 申請印が押されているか否か
    stamp_approved: bool = False  # 承認印が押されているか否か

class PaidLeaveDataList(list):
    """
    有給管理データのリスト
    """
    
    def __init__(self, paid_leave_data: List[PaidLeaveData]):
        super().__init__(paid_leave_data)
        
    def to_date_dict(self) -> dict[str, PaidLeaveData]:
        """
        PaidLeaveDataを日付文字列をキーとする辞書に変換します。
        
        Returns:
            dict[str, PaidLeaveData]: キーが "月_日" 形式の文字列、値がPaidLeaveDataのマッピング
        """
        return {
            f"{data.application_date.month}_{data.application_date.day}": data
            for data in self
        }

