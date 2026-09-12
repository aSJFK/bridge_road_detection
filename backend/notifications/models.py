from django.conf import settings
from django.db import models
from common.models import TimeStampedModel


class Notification(TimeStampedModel):
    """系统通知"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="接收人",
    )
    title = models.CharField("标题", max_length=128)
    content = models.TextField("内容", blank=True, default="")
    is_read = models.BooleanField("已读", default=False, db_index=True)

    class Meta:
        db_table = "notification"
        verbose_name = "系统通知"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class OperationLog(TimeStampedModel):
    """操作日志"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operation_logs",
        verbose_name="操作人",
    )
    operation = models.CharField("操作", max_length=16, default="")
    module = models.CharField("模块", max_length=64, blank=True, default="")
    description = models.CharField("描述", max_length=255, blank=True, default="")
    ip_address = models.CharField("IP 地址", max_length=64, blank=True, default="")

    class Meta:
        db_table = "operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return f"{self.user} {self.operation} {self.module}"
