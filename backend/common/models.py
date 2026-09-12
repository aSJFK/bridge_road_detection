from django.db import models


class TimeStampedModel(models.Model):
    """公共抽象模型：创建/更新时间"""

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True
