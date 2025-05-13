from datetime import date, datetime
from pathlib import Path
from typing import Optional

import xlwings as xw

from njs_mywork_tools.attendance.models.paid_leave_data import (
    PaidLeaveData, PaidLeaveDataList, PaidLeaveType)


class ExcelPaidLeaveReader:
    """
    Excelファイルから有給管理データを読み込むクラス
    """
    
    def __init__(self, file_path: str | Path):
        """
        初期化

        Args:
            file_path: 読み込むExcelファイルのパス
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        self._app: Optional[xw.App] = None
        self._wb: Optional[xw.Book] = None
        self._ws: Optional[xw.Sheet] = None

    def __enter__(self):
        """
        with文でインスタンスを開始する際に呼ばれる

        Returns:
            self: ExcelPaidLeaveReaderインスタンス
        """
        self._app = xw.App(visible=False)
        self._wb = self._app.books.open(self.file_path)
        self._ws = self._wb.sheets["有給休暇管理"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with文でインスタンスを終了する際に呼ばれる

        Args:
            exc_type: 例外の型
            exc_val: 例外の値
            exc_tb: トレースバック
        """
        if self._wb:
            self._wb.close()
        if self._app:
            self._app.quit()

    def _has_stamp_image(self, cell: xw.Range) -> bool:
        """
        指定されたセルに画像が貼り付けられているかを確認する

        Args:
            cell: セル位置

        Returns:
            bool: 画像が存在する場合はTrue
        """
        try:
            if not self._ws:
                raise ValueError("ワークシートが開かれていません")

            # セル内の画像を検索
            shapes = self._ws.shapes
            for shape in shapes:
                # 画像の左上座標がセルの範囲内にあるかチェック
                if (shape.top >= cell.top and 
                    shape.top <= cell.top + (cell.height / 2) and
                    shape.left >= cell.left and 
                    shape.left <= cell.left + (cell.width / 2)
                ):
                    return True
            return False
        except Exception:
            return False

    def _read_paid_leave_type(self, current_row: int) -> PaidLeaveType:
        """
        指定されたセルに有給休暇の種別が記載されているかを確認する

        Args:
            current_row: 行番号

        Returns:
            PaidLeaveType: 有給休暇の種別
        """
        
        # 全日休、午前休、午後休の値を取得
        full_day = bool(self._ws.range(f"O{current_row}").value)
        morning = bool(self._ws.range(f"R{current_row}").value)
        afternoon = bool(self._ws.range(f"U{current_row}").value)
        if full_day:
            return PaidLeaveType.FULL_DAY
        if morning:
            return PaidLeaveType.MORNING
        if afternoon:
            return PaidLeaveType.AFTERNOON
        
        raise ValueError(f"有給休暇の種別が見つかりません: {full_day}, {morning}, {afternoon}")

    def read_paid_leave_sheet(self) -> PaidLeaveDataList:
        """
        有給管理データを読み込む

        Returns
        -------
        PaidLeaveDataList
            読み込んだ有給休暇データ
        """
        try:
            if not self._ws:
                raise ValueError("ワークシートが開かれていません")

            # データをPaidLeaveDataのリストに変換
            paid_leave_data_list = []
            current_row = 10  # 開始行

            while True:
                # A列の値を確認
                date_cell = self._ws.range(f"B{current_row}")
                if not date_cell.value:  # 値が空の場合はループ終了
                    break

                # 日付の取得と変換
                application_date = date_cell.value.date()
                
                # 有給休暇の種別を判定
                leave_type = self._read_paid_leave_type(current_row)

                # 申請印の確認
                stamp_cell = self._ws.range(f"G{current_row}:J{current_row}")
                has_stamp = self._has_stamp_image(stamp_cell)

                # 承認印の確認
                approval_cell = self._ws.range(f"K{current_row}:N{current_row}")
                has_approval = self._has_stamp_image(approval_cell)

                # 有給休暇データを作成
                paid_leave_data = PaidLeaveData(
                    application_date=application_date,
                    leave_type=leave_type,
                    stamp_exists=has_stamp,
                    stamp_approved=has_approval
                )
                paid_leave_data_list.append(paid_leave_data)

                current_row += 1

            return PaidLeaveDataList(paid_leave_data_list)

        except Exception as e:
            raise ValueError(f"有給休暇データの読み込みに失敗しました: {str(e)}")


if __name__ == "__main__":
    with ExcelPaidLeaveReader("./tests/data/paid_leave.xlsx") as reader:
        paid_leave_data_list = reader.read_paid_leave_sheet()
        print(paid_leave_data_list)

