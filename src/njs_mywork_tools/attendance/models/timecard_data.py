from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional


@dataclass
class TimeCardData:
    date: date
    holiday: bool
    work_type: str
    time_in: Optional[time] = None
    time_out: Optional[time] = None
    work_time: Optional[time] = None
    
    def work_type_str(self) -> str:
        if self.work_type in ('在宅', '出勤', '在宅/出勤', '出勤/在宅' ) :
            return '出勤'
        
        if self.work_type in ('有休', '有給'):
            return '有給休暇'

        if self.work_type in ("午前休/在宅", "午前休/出勤"):
            return "午前休"
        
        if self.work_type in ("在宅/午後休", "出勤/午後休"):
            return "午後休"
        
        return ""
    
    def is_attended(self) -> bool:
        """
        出勤したかどうかを判定するメソッド。

        Returns:
            bool: 出勤した場合はTrue、それ以外の場合はFalse
        """
        return self.work_type in (
            '出勤', 
            '在宅/出勤', 
            '出勤/在宅',
            '午前休/出勤',
            '出勤/午後休'
        )

    def is_home_work(self) -> bool:
        """
        在宅勤務かどうかを判定するメソッド。

        Returns:
            bool: 在宅勤務した場合はTrue、それ以外の場合はFalse
        """
        return self.work_type in (
            '在宅',
            '在宅/出勤',
            '出勤/在宅',
            '在宅/午前休',
            '午後休/在宅'
        )

    def remarks_str(self) -> str:
        """
        備考を文字列で返却するメソッド。

        Returns:
            str: 備考の文字列。備考がない場合は空文字列を返す。
        """
        if self.work_type == '在宅/出勤':
            return "午後出社"
        if self.work_type == '出勤/在宅':
            return "午前出社"
        return ''


    def time_in_str(self) -> str:
        return self.time_in.strftime('%H:%M') if self.time_in else ''

    def time_out_str(self) -> str:
        return self.time_out.strftime('%H:%M') if self.time_out else ''

    def overtime_start_time_str(self) -> str:
        if self.time_out and self.time_out > time(17, 30):
            return '17:40'
        return ''

    def overtime_end_time_str(self) -> str:
        if self.time_out and self.time_out > time(17, 30):
            return self.time_out.strftime('%H:%M')
        return ''


class TimeCardDataList(list):
    def __init__(self, time_cards: List[TimeCardData]):
        super().__init__(time_cards)
        
    def to_date_dict(self) -> dict[str, TimeCardData]:
        """TimeCardDataを日付文字列をキーとする辞書に変換します。
        
        Returns:
            dict[str, TimeCardData]: キーが "月_日" 形式の文字列、値がTimeCardDataのマッピング
        """
        return {
            f"{data.date.month}_{data.date.day}": data 
            for data in self
        }
    


