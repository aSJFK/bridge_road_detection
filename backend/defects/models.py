from django.db import models
from common.models import TimeStampedModel

DEFECT_TYPE_CHOICES = [
    ("crack", "裂缝"),
    ("spalling", "剥落"),
    ("pothole", "坑洞"),
    ("corrosion", "钢筋锈蚀"),
    ("other", "其他"),
]


class Defect(TimeStampedModel):
    """缺陷结果：保存检测框坐标"""

    image = models.ForeignKey(
        "detection.DetectionImage",
        on_delete=models.CASCADE,
        related_name="defects",
        verbose_name="所属图片",
    )
    defect_type = models.CharField("缺陷类型", max_length=32, choices=DEFECT_TYPE_CHOICES, db_index=True)
    source = models.CharField("检测模型来源", max_length=16, default="bridge", db_index=True)  # bridge / road
    confidence = models.FloatField("置信度", default=0.0)
    x1 = models.FloatField("左上角 x", default=0)
    y1 = models.FloatField("左上角 y", default=0)
    x2 = models.FloatField("右下角 x", default=0)
    y2 = models.FloatField("右下角 y", default=0)
    area = models.FloatField("面积", default=0)

    class Meta:
        db_table = "defect"
        verbose_name = "缺陷"
        verbose_name_plural = verbose_name
        ordering = ["-confidence"]
        indexes = [models.Index(fields=["defect_type", "confidence"])]

    def __str__(self):
        return f"{self.get_defect_type_display()} {self.confidence:.2f}"
