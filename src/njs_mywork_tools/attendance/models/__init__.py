"""
Attendance models package for data structures
""" 

from .employee import Employee
from .timecard_data import TimeCardData, TimeCardDataList

__all__ = [
    "Employee",
    "TimeCardData",
    "TimeCardDataList",
]
