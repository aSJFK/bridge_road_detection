from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ("admin", "管理员"),
    ("user", "普通用户"),
]


class User(AbstractUser):
    """自定义用户：使用 Django 认证系统（密码加密存储）"""

    role = models.CharField("角色", max_length=20, choices=ROLE_CHOICES, default="user")
    avatar = models.ImageField("头像", upload_to="avatars/", null=True, blank=True)
    phone = models.CharField("手机号", max_length=20, blank=True, default="")
    # 用户准确率（百分比）：首次登录初始化为 90~95 随机值，后续只升不降
    accuracy = models.FloatField("准确率", default=0.0)

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __str__(self):
        return self.username
