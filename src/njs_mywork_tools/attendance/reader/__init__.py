"""
Attendance reader package for input operations
"""

from .excel_paid_leave_reader import ExcelPaidLeaveReader
from .excel_timecard_reader import ExcelTimeCardReader
from .google_timecard_reader import GoogleTimeCardReader
from .timecard_reader import TimeCardReader

__all__ = [
    "ExcelTimeCardReader",
    "GoogleTimeCardReader",
    "TimeCardReader",
    "ExcelPaidLeaveReader",
]

__version__ = "0.1.0"
