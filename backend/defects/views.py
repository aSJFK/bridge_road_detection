from common.viewsets import ApiReadOnlyModelViewSet
from .models import Defect
from detection.serializers import DefectSerializer


class DefectViewSet(ApiReadOnlyModelViewSet):
    """缺陷管理：只读，支持搜索/过滤"""

    queryset = Defect.objects.select_related("image__task").all()
    serializer_class = DefectSerializer
    filterset_fields = ["defect_type", "image__task"]
    search_fields = ["defect_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == "user":
            qs = qs.filter(image__task__created_by=user)
        return qs
