from rest_framework import serializers
from detection.models import DetectionImage
from detection.serializers import DefectSerializer, DetectionImageSerializer
from .models import InspectionReport, ReportRating


class ReportRatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, default="")
    user_role = serializers.CharField(source="user.role", read_only=True, default="")

    class Meta:
        model = ReportRating
        fields = [
            "id",
            "report",
            "user",
            "username",
            "user_role",
            "score",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "report", "user", "username", "user_role", "created_at"]

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("评分必须在 1~5 之间")
        return value


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True, default="")
    task_name = serializers.CharField(source="task.task_name", read_only=True, default="")
    image_url = serializers.SerializerMethodField()
    result_url = serializers.SerializerMethodField()
    average_score = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    my_rating = serializers.SerializerMethodField()

    class Meta:
        model = InspectionReport
        fields = [
            "id",
            "task",
            "task_name",
            "report_name",
            "total_images",
            "total_defects",
            "accuracy",
            "report_file",
            "image_url",
            "result_url",
            "average_score",
            "rating_count",
            "my_rating",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["created_by"]

    def get_image_url(self, obj):
        if obj.image and obj.image.original_image:
            return obj.image.original_image.url if obj.image.original_image.name else None
        return None

    def get_result_url(self, obj):
        if obj.image and obj.image.result_image:
            return obj.image.result_image.url if obj.image.result_image.name else None
        return None

    def get_my_rating(self, obj):
        """当前登录用户对这份报告的评价"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        rating = obj.ratings.filter(user=request.user).first()
        if rating:
            return ReportRatingSerializer(rating).data
        return None


class ReportDetailSerializer(ReportSerializer):
    """报告详情：附加图片缺陷明细"""

    defects = serializers.SerializerMethodField()

    class Meta(ReportSerializer.Meta):
        fields = ReportSerializer.Meta.fields + ["defects"]

    def get_defects(self, obj):
        if obj.image:
            return DefectSerializer(obj.image.defects.all(), many=True).data
        return []
