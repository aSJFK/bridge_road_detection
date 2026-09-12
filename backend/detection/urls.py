from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DetectionTaskViewSet, PredictView

router = DefaultRouter()
router.register(r"tasks", DetectionTaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    # 兼容前端约定的 /api/detection/recent/ 与 /api/detection/predict/
    path("recent/", DetectionTaskViewSet.as_view({"get": "recent"}), name="detection-recent"),
    path("predict/", PredictView.as_view(), name="predict"),
]
