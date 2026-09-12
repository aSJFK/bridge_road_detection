from rest_framework.permissions import IsAuthenticated
from common.viewsets import ApiModelViewSet
from .models import Dataset
from .serializers import DatasetSerializer


class DatasetViewSet(ApiModelViewSet):
    """数据集管理"""

    queryset = Dataset.objects.select_related("created_by").all()
    serializer_class = DatasetSerializer
    search_fields = ["name", "description"]

    def get_permissions(self):
        # 数据集对所有登录用户开放
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
