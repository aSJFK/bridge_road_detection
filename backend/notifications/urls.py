from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, OperationLogViewSet

# NotificationViewSet 挂载在 notifications/ 下（含 unread-count 等 action）
router = DefaultRouter()
router.register(r"messages", NotificationViewSet, basename="notification")
router.register(r"logs", OperationLogViewSet, basename="oplog")

urlpatterns = [
    path("", include(router.urls)),
    # 兼容前端约定的 GET /api/notifications/unread-count/
    path("unread-count/", NotificationViewSet.as_view({"get": "unread_count"}), name="notification-unread-count"),
]
