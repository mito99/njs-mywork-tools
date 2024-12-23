import tempfile
import xlwings as xw
import pandas as pd
from pathlib import Path
from create_shokuin import create_shokuin

def write_to_excel():
    # 出力先のパスを設定
    output_path = Path(__file__).parent.parent / 'tests' / 'data' / 'output.xlsx'

    try:
        with xw.App(visible=True, add_book=False) as app:
            with app.books.open(output_path) as wb:
                sheet = wb.sheets['11月']
                sheet.activate()
                
                sheet.range('F10').value = '出勤'
                sheet.range('L10').value = '17:40'
                sheet.range('M10').value = '18:40'

                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    syokuin_image = create_shokuin('山田', '2024.12.22', '太郎', size=300)
                    syokuin_image.save(tmp.name)
                    sheet.pictures.add(
                        tmp.name,
                        left=sheet.range('S4').left - 5,
                        top=sheet.range('S4').top - 5,
                        width=70,
                        height=70,
                    )
                
                # 保存
                # wb.save()
            
        print(f"データを {output_path} に保存しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    write_to_excel()
