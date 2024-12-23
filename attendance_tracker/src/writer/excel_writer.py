"""
処理結果をExcelファイルに出力するモジュール
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .. import settings


class ExcelWriter:
    """
    処理結果をExcelファイルに出力するクラス
    """

    def __init__(self, template_path: Path):
        """
        初期化

        Args:
            template_path: テンプレートExcelファイルのパス
        """
        self.template_path = template_path

    def write(self, df: pd.DataFrame, output_path: Path = None) -> None:
        """
        DataFrameをExcelファイルに出力する

        Args:
            df: 出力するDataFrame
            output_path: 出力先のパス（省略時はテンプレートと同じディレクトリに出力）
        """
        try:
            if output_path is None:
                output_path = (
                    self.template_path.parent
                    / f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )

            # Excelファイルに出力
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=settings.SHEET_NAME, index=False)

        except Exception as e:
            raise RuntimeError(f"Excelファイルの出力に失敗しました: {str(e)}")
