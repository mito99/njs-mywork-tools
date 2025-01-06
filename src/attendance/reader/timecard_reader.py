from abc import ABC, abstractmethod
from datetime import date

from attendance.models.timecard_data import TimeCardDataList


class TimeCardReader(ABC):

    @abstractmethod
    def read_timecard_sheet(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> TimeCardDataList:
        pass
