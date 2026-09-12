"""结果图片绘制：在检测框上绘制缺陷类型、置信度

双模型融合绘制：
  - 来源 bridge（桥梁模型）使用蓝色系
  - 来源 road（公路模型）使用橙色系
  - 标签前缀标注来源，便于用户区分
"""
from io import BytesIO

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

DEFECT_META = settings.DEFECT_META

# 来源 -> 边框颜色（RGB）
SOURCE_COLORS = {
    "bridge": (30, 144, 255),  # 蓝
    "road": (255, 140, 26),    # 橙
}

# 来源中文名
SOURCE_LABELS = {"bridge": "桥梁", "road": "公路"}


def _load_font(size: int):
    """尝试加载中文字体，失败则使用默认字体"""
    font_candidates = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def annotate(image: Image.Image, predictions: list) -> Image.Image:
    """在图片上绘制检测框，返回标注后的图片

    predictions 的 bbox 为归一化坐标（0~1），绘制时按图片实际尺寸还原。
    """
    draw = ImageDraw.Draw(image)
    font = _load_font(16)
    width, height = image.size

    for p in predictions:
        x1, y1, x2, y2 = [float(v) for v in p["bbox"]]
        meta = DEFECT_META.get(p["type"], DEFECT_META["other"])
        source = p.get("source", "bridge")
        color = SOURCE_COLORS.get(source, SOURCE_COLORS["bridge"])
        source_label = SOURCE_LABELS.get(source, "桥梁")
        label = f"{source_label}-{meta['label']} {p['confidence']:.2f}"

        # 归一化 -> 像素坐标
        px1, py1 = x1 * width, y1 * height
        px2, py2 = x2 * width, y2 * height

        draw.rectangle([px1, py1, px2, py2], outline=color, width=3)
        # 标签背景
        text_bbox = draw.textbbox((px1, py1), label, font=font)
        draw.rectangle(
            [text_bbox[0] - 3, text_bbox[1] - 3, text_bbox[2] + 3, text_bbox[3] + 3],
            fill=color,
        )
        draw.text((text_bbox[0], text_bbox[1]), label, fill="white", font=font)

    return image


def save_result_image(image: Image.Image, result_path) -> None:
    """保存标注结果图"""
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=90)
    with open(result_path, "wb") as f:
        f.write(buf.getvalue())
