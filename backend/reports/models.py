from django.conf import settings
from django.db import models
from common.models import TimeStampedModel


class InspectionReport(TimeStampedModel):
    """检测报告"""

    # 报告关联的检测任务（一次上传一张图 -> 一个任务 -> 一份报告）
    task = models.ForeignKey(
        "detection.DetectionTask",
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="关联任务",
        null=True,
        blank=True,
    )
    image = models.ForeignKey(
        "detection.DetectionImage",
        on_delete=models.SET_NULL,
        related_name="reports",
        verbose_name="关联图片",
        null=True,
        blank=True,
    )
    report_name = models.CharField("报告名称", max_length=128, default="")
    total_images = models.PositiveIntegerField("图片总数", default=0)
    total_defects = models.PositiveIntegerField("缺陷总数", default=0)
    accuracy = models.FloatField("平均置信度", default=0.0)
    report_file = models.FileField("报告文件", upload_to="reports/", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspection_reports",
        verbose_name="创建人",
    )

    class Meta:
        db_table = "inspection_report"
        verbose_name = "检测报告"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.report_name

    @property
    def average_score(self):
        """报告平均评分（保留1位）"""
        agg = self.ratings.aggregate(avg=models.Avg("score"))
        return round(agg["avg"], 1) if agg["avg"] is not None else None

    @property
    def rating_count(self):
        return self.ratings.count()


class ReportRating(TimeStampedModel):
    """报告评价（评分 + 评论）

    业务规则：
      - 每个用户对同一份报告只能评价一次（unique report+user）
      - 用户提交后不可修改、不可删除（只能查看）
      - 管理员可修改、删除任意评价
    """

    report = models.ForeignKey(
        InspectionReport,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="所属报告",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="report_ratings",
        verbose_name="评价人",
    )
    score = models.PositiveSmallIntegerField("评分", default=5)  # 1~5
    comment = models.TextField("评价内容", blank=True, default="")

    class Meta:
        db_table = "report_rating"
        verbose_name = "报告评价"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["report", "user"],
                name="uniq_report_user_rating",
            )
        ]

    def __str__(self):
        return f"报告{self.report_id} 评分{self.score}"
