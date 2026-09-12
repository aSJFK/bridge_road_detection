"""报告文件生成：把检测结果渲染成可下载的 HTML 报告"""

import html
from datetime import datetime

from django.conf import settings


DEFECT_LABELS = dict(settings.DEFECT_META)
SOURCE_LABELS = {"bridge": "桥梁模型", "road": "公路模型"}


def build_report_html(report, image, defects) -> str:
    """生成检测报告 HTML 字符串"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    result_url = image.result_image.url if image.result_image and image.result_image.name else ""

    rows = ""
    for d in defects:
        meta = DEFECT_LABELS.get(d.defect_type, {"label": d.defect_type})
        src = SOURCE_LABELS.get(d.source, d.source)
        rows += f"""
        <tr>
            <td>{html.escape(src)}</td>
            <td>{html.escape(meta['label'])}</td>
            <td>{d.confidence:.3f}</td>
            <td>[{d.x1:.3f}, {d.y1:.3f}, {d.x2:.3f}, {d.y2:.3f}]</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{html.escape(report.report_name)}</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; background: #fff; color: #222; margin: 0; padding: 24px; }}
  h1 {{ color: #1e90ff; border-bottom: 3px solid #1e90ff; padding-bottom: 10px; }}
  .meta {{ color: #666; margin-bottom: 16px; }}
  .stat {{ display: flex; gap: 32px; margin: 16px 0; }}
  .stat div {{ font-size: 15px; }}
  .stat b {{ font-size: 22px; color: #1e90ff; }}
  img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 8px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f0f7ff; }}
  .legend {{ font-size: 13px; color: #555; margin: 8px 0; }}
</style>
</head>
<body>
  <h1>{html.escape(report.report_name)}</h1>
  <p class="meta">生成时间：{now} | 报告编号：#REP-{report.id:05d} | 检测人：{html.escape(report.created_by.username if report.created_by else '-')}</p>

  <div class="stat">
    <div>检测图片<b>{report.total_images}</b></div>
    <div>缺陷总数<b>{report.total_defects}</b></div>
    <div>平均置信度<b>{report.accuracy * 100:.1f}%</b></div>
  </div>

  <p class="legend">标注图（蓝色=桥梁模型，橙色=公路模型）</p>
  <img src="{html.escape(result_url)}" alt="检测结果标注图">

  <h2>缺陷明细</h2>
  <table>
    <thead>
      <tr><th>来源</th><th>缺陷类型</th><th>置信度</th><th>坐标</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <p style="color:#999; margin-top:24px;">本报告由桥路缺陷检测系统自动生成</p>
</body>
</html>"""


def save_report_file(report, image, defects, file_rel) -> str:
    """保存报告 HTML 文件，返回相对路径"""
    content = build_report_html(report, image, defects)
    file_path = settings.MEDIA_ROOT / file_rel
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_rel
