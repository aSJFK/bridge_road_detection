from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, ReportRatingView

router = DefaultRouter()
router.register(r"", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
    # 评价修改/删除（仅管理员）
    path("ratings/<int:pk>/", ReportRatingView.as_view(), name="rating-detail"),
]
