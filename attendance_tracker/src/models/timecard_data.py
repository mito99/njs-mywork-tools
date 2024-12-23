from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class TimeCardData:
    date: datetime
    holiday: bool
    work_type: str
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None