from rest_framework import serializers
from .models import Notification, OperationLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "content", "is_read", "created_at"]


class OperationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, default="")

    class Meta:
        model = OperationLog
        fields = ["id", "username", "operation", "module", "description", "ip_address", "created_at"]
