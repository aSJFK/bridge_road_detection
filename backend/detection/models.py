from django.conf import settings
from django.db import models
from common.models import TimeStampedModel

TASK_STATUS_CHOICES = [
    ("pending", "待检测"),
    ("running", "检测中"),
    ("completed", "已完成"),
    ("failed", "失败"),
]


class DetectionTask(TimeStampedModel):
    """检测任务（单图检测）"""

    task_name = models.CharField("任务名称", max_length=128, default="")
    model_name = models.CharField("模型名称", max_length=64, blank=True, default="yolov8")
    model_version = models.CharField("模型版本", max_length=32, blank=True, default="v1")
    image_count = models.PositiveIntegerField("图片数量", default=0)
    defect_count = models.PositiveIntegerField("缺陷数量", default=0)
    accuracy = models.FloatField("平均置信度", default=0.0)
    status = models.CharField("状态", max_length=20, choices=TASK_STATUS_CHOICES, default="pending", db_index=True)
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detection_tasks",
        verbose_name="创建人",
    )

    class Meta:
        db_table = "detection_task"
        verbose_name = "检测任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return self.task_name or f"任务-{self.pk}"


class DetectionImage(TimeStampedModel):
    """检测图片"""

    task = models.ForeignKey(
        DetectionTask,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="所属任务",
    )
    original_image = models.ImageField("原图", upload_to="detection/original/")
    result_image = models.ImageField("结果图", upload_to="detection/result/", null=True, blank=True)
    image_width = models.PositiveIntegerField("图片宽度", default=0)
    image_height = models.PositiveIntegerField("图片高度", default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detection_images",
        verbose_name="上传人",
    )

    class Meta:
        db_table = "detection_image"
        verbose_name = "检测图片"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"图片-{self.pk}"
