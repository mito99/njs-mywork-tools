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
    
    def work_type_str(self) -> str:
        if self.work_type in ('在宅', '出勤') :
            return '出勤'
        
        if self.work_type in ('有休', '有給'):
            return '有給休暇'
        
        return ""

    def time_in_str(self) -> str:
        return self.time_in.strftime('%H:%M') if self.time_in else ''

    def time_out_str(self) -> str:
        return self.time_out.strftime('%H:%M') if self.time_out else ''


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
    


