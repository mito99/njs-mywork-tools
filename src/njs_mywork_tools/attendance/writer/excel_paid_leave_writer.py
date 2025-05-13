import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import List, TypedDict

import xlwings as xw

from njs_mywork_tools.attendance.models.employee import Employee
from njs_mywork_tools.attendance.models.paid_leave_data import (PaidLeaveData,
                                                                PaidLeaveType)
from njs_mywork_tools.utils.shokuin import create_shokuin


class ConfigDict(TypedDict):
    xlwings_visible: bool

class ExcelPaidLeaveWriter:
    """
    有給管理ツールのメインパッケージ
    """

    def __init__(self, template_path: Path, employee: Employee, config: ConfigDict ={
        "xlwings_visible": False
    }):
        self.template_path = template_path
        self.employee = employee
        self.xlwings_visible = config.get("xlwings_visible", False)
        self.paid_leave_data_list: List[PaidLeaveData] = []

    def __enter__(self):
        """
        with文でインスタンスを開始する際に呼ばれる
        """
        self._app = xw.App(visible=self.xlwings_visible)
        self._wb = self._app.books.open(self.template_path)
        self._ws = self._wb.sheets["有給休暇管理"]
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with文でインスタンスを終了する際に呼ばれる
        """
        if self._wb:
            self._wb.close()
        if self._app:
            self._app.quit()

    def add_paid_leave_application(self, app_date: date, leave_type: PaidLeaveType) -> None:
        """
        有給休暇の申請を追加する

        Args:
            application_date (date): 有給休暇の申請日
            leave_type (PaidLeaveType): 有給休暇の種類
        """
        
        try:
            if not self._ws:
                raise ValueError("ワークシートが開かれていません")
            
            # 有給休暇の申請日の行を取得する
            date_list = self._ws.range("B10:B54").value
            date_list = [x for x in (date_list if date_list else []) if x]
            hit_index = [i for i,x in enumerate(date_list) if x.date() == app_date]
            current_row = (hit_index[0] if hit_index else len(date_list)) + 10
           
            # 出勤印を押す
            today = datetime.now().strftime("%Y.%m.%d")
            self._stamp_syokuin(
                self._ws, 
                f"G{current_row}", 
                "JS", 
                today,
                self.employee.family_name
            )
            
            # 有給休暇の申請を追加する
            self._ws.range(f"B{current_row}").value = app_date
            self._ws.range(f"O{current_row}").value = "1" if leave_type == PaidLeaveType.FULL_DAY else ""
            self._ws.range(f"R{current_row}").value = "1" if leave_type == PaidLeaveType.MORNING else ""
            self._ws.range(f"U{current_row}").value = "1" if leave_type == PaidLeaveType.AFTERNOON else ""

            self._wb.save()
        except Exception as e:
            raise ValueError(f"有給休暇の申請を追加する際にエラーが発生しました: {str(e)}")
        

    def add_paid_leave_applications(self, data: dict[date, PaidLeaveType]) -> None:
        """
        複数の有給休暇の申請を一括で追加する

        Args:
            data (dict[date, PaidLeaveType]): 追加する有給休暇データの辞書
        """
        for app_date, leave_type in data.items():
            self.add_paid_leave_application(app_date, leave_type)

    def _stamp_syokuin(
        self, sheet: xw.Sheet, cell: str, text1: str, text2: str, text3: str
    ) -> None:
        """
        出勤印を押す
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            syokuin_image = create_shokuin(text1, text2, text3, size=300)
            syokuin_image.save(tmp.name)

            name = f"syokuin_{cell}"
            for pic in sheet.pictures:
                if pic.name == name:
                    pic.delete()

            sheet.pictures.add(
                tmp.name,
                left=sheet.range(cell).left - 5,
                top=sheet.range(cell).top - 5,
                width=50,
                height=50,
                name=name,
            )

if __name__ == "__main__":
    path = Path("tests/data/paid_leave.xlsx")
    employee = Employee(
        family_name="山田",
        given_name="太郎"
    )

    with ExcelPaidLeaveWriter(path, employee) as writer:
        # writer.add_paid_leave_application(
        #     app_date=date(2025, 5, 11),
        #     leave_type=PaidLeaveType.FULL_DAY
        # )

        data = {
            date(2025, 5, 11): PaidLeaveType.FULL_DAY,
            date(2025, 5, 12): PaidLeaveType.MORNING,
            date(2025, 5, 13): PaidLeaveType.AFTERNOON
        }
        writer.add_paid_leave_applications(data)

