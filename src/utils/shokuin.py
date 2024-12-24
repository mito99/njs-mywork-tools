from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

def _draw_circle(draw, size, radius, center):
    """背景の円を描画する"""
    draw.ellipse(
        [
            center - radius,
            center - radius,
            center + radius,
            center + radius
        ],
        fill=None,
        outline='red',
        width=5
    )

def _draw_text(draw, text, size, radius, center, area="top"):
    """テキストを描画する
    
    Parameters:
        area: "top", "center", "bottom" のいずれか
        - top: 円の上部 1/4 の位置
        - center: 円の中心位置
        - bottom: 円の下部 3/4 の位置
    """
    if area == "top":
        font_size = int(radius * 0.55)
    elif area == "center":
        font_size = int(radius * 0.38)
    elif area == "bottom":
        font_size = int(radius * 0.45)
    
    try:
        font = ImageFont.truetype("msmincho.ttc", font_size)
        # font = ImageFont.truetype("msgothic.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # X座標は中央揃え
    x = (size - text_width) // 2
    
    # Y座標を計算
    margin = (size - 2 * radius) / 2  # 円の外側のマージン
    effective_height = 2 * radius      # 円の実効的な高さ
    
    if area == "top":
        y = margin + (effective_height * 0.13) - (text_height / 2)
    elif area == "center":
        y = margin + (effective_height * 0.47) - (text_height / 2)
    elif area == "bottom":
        y = margin + (effective_height * 0.8) - (text_height / 2)
    
    draw.text((x, y), text, font=font, fill='red')

def _draw_horizontal_lines(draw, radius, center):
    """横線を描画する"""
    line_y_positions = [
        center - radius/3,
        center + radius/3
    ]
    
    for y_pos in line_y_positions:
        y_offset = abs(y_pos - center)
        x_length = np.sqrt(radius * radius - y_offset * y_offset)
        
        draw.line(
            [
                (center - x_length, y_pos),
                (center + x_length, y_pos)
            ],
            fill='red',
            width=5
        )

def create_shokuin(text1, text2, text3,size=200, margin_ratio=0.1, border_width_ratio=0.03) -> Image:
    """職印画像を生成する"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    radius = size * (1 - 2 * margin_ratio) / 2
    center = size / 2
    
    _draw_circle(draw, size, radius, center)
    _draw_horizontal_lines(draw, radius, center)

    _draw_text(draw, text1, size, radius, center, area="top")
    _draw_text(draw, text2, size, radius, center, area="center")
    _draw_text(draw, text3, size, radius, center, area="bottom")

    return img.filter(ImageFilter.SMOOTH)

if __name__ == "__main__":
    text1 = "JS"
    text2 = "2024.12.22"
    text3 = "みと"
    img = create_shokuin(text1, text2, text3, size=400)
    img.save("./tmp/shokuin.png")

