from django.contrib import admin
from .models import DetectionImage, DetectionTask


@admin.register(DetectionTask)
class DetectionTaskAdmin(admin.ModelAdmin):
    list_display = ("task_name", "status", "image_count", "defect_count", "accuracy", "created_at")
    list_filter = ("status",)


@admin.register(DetectionImage)
class DetectionImageAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "image_width", "image_height", "created_at")
