from rest_framework import serializers
from .models import DetectionImage, DetectionTask
from defects.models import Defect


class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = ["id", "defect_type", "source", "confidence", "x1", "y1", "x2", "y2", "area", "created_at"]


class DetectionImageSerializer(serializers.ModelSerializer):
    defects = DefectSerializer(many=True, read_only=True)

    class Meta:
        model = DetectionImage
        fields = ["id", "original_image", "result_image", "image_width", "image_height", "defects", "created_at"]


class DetectionTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionTask
        fields = [
            "id",
            "task_name",
            "model_name",
            "model_version",
            "image_count",
            "defect_count",
            "accuracy",
            "status",
            "started_at",
            "completed_at",
            "created_at",
        ]


class DetectionTaskDetailSerializer(DetectionTaskListSerializer):
    images = DetectionImageSerializer(many=True, read_only=True)

    class Meta(DetectionTaskListSerializer.Meta):
        fields = DetectionTaskListSerializer.Meta.fields + ["images"]
