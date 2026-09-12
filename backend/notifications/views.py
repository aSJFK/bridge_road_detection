from rest_framework.decorators import action

from accounts.permissions import IsAdmin
from common.responses import ok
from common.viewsets import ApiReadOnlyModelViewSet
from .models import Notification, OperationLog
from .serializers import NotificationSerializer, OperationLogSerializer


class NotificationViewSet(ApiReadOnlyModelViewSet):
    """系统通知：只查看自己的通知"""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """未读通知数：GET /api/notifications/unread-count/"""
        count = self.get_queryset().filter(is_read=False).count()
        return ok(data={"count": count})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """全部标记已读"""
        self.get_queryset().update(is_read=True)
        return ok(data=None, message="已全部标记为已读")


class OperationLogViewSet(ApiReadOnlyModelViewSet):
    """操作日志：仅管理员"""

    queryset = OperationLog.objects.select_related("user").all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdmin]
    search_fields = ["module", "description", "user__username"]
