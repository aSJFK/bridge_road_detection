from rest_framework import parsers, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin
from common.responses import ok, fail
from common.viewsets import ApiModelViewSet
from .models import InspectionReport, ReportRating
from .serializers import ReportDetailSerializer, ReportRatingSerializer, ReportSerializer


class ReportViewSet(ApiModelViewSet):
    """检测报告管理"""

    queryset = (
        InspectionReport.objects.select_related("task", "image", "created_by")
        .prefetch_related("ratings__user")
        .all()
    )
    serializer_class = ReportSerializer
    search_fields = ["report_name"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReportDetailSerializer
        return ReportSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == "user":
            qs = qs.filter(created_by=user)
        # 支持按任务过滤：?task=<id>
        task_id = self.request.query_params.get("task")
        if task_id:
            qs = qs.filter(task_id=task_id)
        # 支持按日期范围过滤：?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ---------- 评价相关 ----------

    @action(detail=True, methods=["post"], url_path="rate")
    def rate(self, request, pk=None):
        """提交评价：POST /api/reports/{id}/rate/

        body: {score: 1~5, comment: str}
        每个用户只能评价一次，提交后不可修改/删除（管理员除外）。
        """
        report = self.get_object()
        if report.ratings.filter(user=request.user).exists():
            return fail("您已评价过该报告，提交后不可修改", 400)

        serializer = ReportRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report, user=request.user)
        return ok(data=serializer.data, message="评价已提交，提交后无法修改", code=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="ratings")
    def ratings(self, request, pk=None):
        """评价列表：GET /api/reports/{id}/ratings/（所有登录用户可查看）"""
        report = self.get_object()
        qs = report.ratings.select_related("user").all()
        return ok(data=ReportRatingSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], url_path="my-rating")
    def my_rating(self, request, pk=None):
        """当前用户的评价：GET /api/reports/{id}/my-rating/"""
        report = self.get_object()
        rating = report.ratings.filter(user=request.user).first()
        if not rating:
            return ok(data=None)
        return ok(data=ReportRatingSerializer(rating).data)


class ReportRatingView(APIView):
    """单条评价的操作：仅管理员可修改/删除"""

    permission_classes = [IsAdmin]

    def get_object(self, rating_id):
        try:
            return ReportRating.objects.select_related("user").get(id=rating_id)
        except ReportRating.DoesNotExist:
            return None

    def put(self, request, pk):
        rating = self.get_object(pk)
        if not rating:
            return fail("评价不存在", 404)
        serializer = ReportRatingSerializer(rating, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ok(data=serializer.data, message="评价已更新")

    def delete(self, request, pk):
        rating = self.get_object(pk)
        if not rating:
            return fail("评价不存在", 404)
        rating.delete()
        return ok(data=None, message="评价已删除")
