"""初始化数据库：创建管理员/测试用户 + 示例数据

用法: python manage.py init_data
"""
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from detection.models import DetectionImage, DetectionTask
from defects.models import Defect
from datasets.models import Dataset
from notifications.models import Notification

DEFECT_TYPES = ["crack", "spalling", "pothole", "corrosion", "other"]


class Command(BaseCommand):
    help = "初始化桥路缺陷检测系统数据（管理员、测试用户、示例项目/任务/缺陷）"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("== 创建用户 ==")
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"role": "admin", "email": "admin@bridge.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin123456")
            admin.save()
            self.stdout.write("  创建管理员 admin / admin123456")
        else:
            self.stdout.write("  管理员已存在")

        normal, _ = User.objects.get_or_create(
            username="testuser",
            defaults={"role": "user", "email": "user@bridge.com"},
        )
        normal.set_password("user123456")
        normal.save()
        self.stdout.write("  创建 testuser")

        if DetectionTask.objects.exists():
            self.stdout.write(self.style.WARNING("示例数据已存在，跳过"))
            return

        self.stdout.write("== 创建示例任务 ==")
        for i in range(10):
            task = DetectionTask.objects.create(
                task_name=f"检测任务-{i + 1:02d}",
                model_name="yolov8",
                model_version="v1",
                image_count=random.randint(60, 220),
                defect_count=random.randint(10, 45),
                accuracy=round(random.uniform(0.85, 0.99), 3),
                status="completed",
                started_at=timezone.now() - timezone.timedelta(days=random.randint(0, 6), hours=random.randint(0, 20)),
                completed_at=timezone.now() - timezone.timedelta(days=random.randint(0, 6), hours=random.randint(0, 20)),
                created_by=admin,
            )
            task.created_at = timezone.now() - timezone.timedelta(days=random.randint(0, 6), hours=random.randint(1, 23))
            task.save(update_fields=["created_at"])

            # 每个任务关联图片记录（无实际文件，仅用于统计）
            for _ in range(3):
                img = DetectionImage.objects.create(
                    task=task,
                    original_image=f"detection/original/seed_{task.id}.jpg",
                    image_width=1920,
                    image_height=1080,
                    created_by=admin,
                )
                for _ in range(random.randint(1, 4)):
                    x1 = random.uniform(0.1, 0.5)
                    y1 = random.uniform(0.1, 0.5)
                    x2 = min(0.98, x1 + random.uniform(0.2, 0.4))
                    y2 = min(0.98, y1 + random.uniform(0.2, 0.4))
                    Defect.objects.create(
                        image=img,
                        defect_type=random.choice(DEFECT_TYPES),
                        confidence=round(random.uniform(0.55, 0.98), 3),
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        area=(x2 - x1) * (y2 - y1),
                    )
        self.stdout.write("  创建 10 个检测任务 + 示例缺陷")

        self.stdout.write("== 创建示例数据集 ==")
        Dataset.objects.create(
            name="桥梁缺陷数据集 v1",
            description="桥梁表面裂缝/剥落/锈蚀标注数据集",
            image_count=12500,
            annotation_count=23800,
            version="v1.0",
            status="active",
            created_by=admin,
        )
        Dataset.objects.create(
            name="道路坑洞数据集",
            description="道路坑洞与裂缝检测训练数据",
            image_count=8600,
            annotation_count=15200,
            version="v1.2",
            status="active",
            created_by=admin,
        )

        self.stdout.write("== 创建示例通知 ==")
        Notification.objects.create(
            user=admin,
            title="检测任务完成",
            content="XX大桥巡检任务已完成，共发现 23 处缺陷，请及时查看报告。",
        )
        Notification.objects.create(
            user=admin,
            title="模型更新",
            content="YOLOv8 检测模型已更新至 v1.0，平均准确率 96.7%。",
        )
        Notification.objects.create(
            user=admin,
            title="系统维护",
            content="系统将于本周日凌晨 2:00-4:00 进行例行维护。",
        )

        self.stdout.write(self.style.SUCCESS("数据初始化完成"))
        self.stdout.write("  管理员: admin / admin123456")
        self.stdout.write("  普通用户: testuser / user123456")
