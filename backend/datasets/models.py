from django.db import models
from common.models import TimeStampedModel

DATASET_STATUS_CHOICES = [
    ("draft", "草稿"),
    ("active", "启用"),
    ("archived", "已归档"),
]


class Dataset(TimeStampedModel):
    """数据集"""

    name = models.CharField("数据集名称", max_length=128, db_index=True)
    description = models.TextField("描述", blank=True, default="")
    image_count = models.PositiveIntegerField("图片数量", default=0)
    annotation_count = models.PositiveIntegerField("标注数量", default=0)
    version = models.CharField("版本", max_length=32, default="v1.0")
    status = models.CharField("状态", max_length=20, choices=DATASET_STATUS_CHOICES, default="draft", db_index=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
        verbose_name="创建人",
    )

    class Meta:
        db_table = "dataset"
        verbose_name = "数据集"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
