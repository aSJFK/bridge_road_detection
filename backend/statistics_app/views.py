"""统计接口：首页统计、缺陷类型分布

数据范围规则：
  - 管理员（admin）→ 全部数据库记录
  - 普通用户（user）→ 仅自己提交的检测（created_by = 当前用户）
"""
from datetime import timedelta

from django.db.models import Count, Max, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.responses import ok
from detection.models import DetectionTask
from defects.models import Defect


def _tasks_for_user(request):
    """按角色返回任务查询集：普通用户只取自己的，管理员取全部"""
    qs = DetectionTask.objects.all()
    user = request.user
    if user.is_authenticated and user.role == "user":
        qs = qs.filter(created_by=user)
    return qs


def _defects_for_user(request):
    """按角色返回缺陷查询集：普通用户只取自己任务下的缺陷"""
    qs = Defect.objects.all()
    user = request.user
    if user.is_authenticated and user.role == "user":
        qs = qs.filter(image__task__created_by=user)
    return qs


class HomeStatisticsView(APIView):
    """首页统计：GET /api/home/statistics/

    返回: image_count, defect_count, accuracy
    普通用户只统计自己提交的检测，管理员统计全部。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = _tasks_for_user(request)
        defects = _defects_for_user(request)

        image_count = tasks.aggregate(total=Sum("image_count"))["total"] or 0
        defect_count = defects.count()

        # 准确率：首次登录初始化为 90~95，之后取（初始值, 检测最高置信度）的较大者，只升不降
        max_conf = defects.aggregate(m=Max("confidence"))["m"]
        conf_acc = round((max_conf or 0) * 100, 1)
        accuracy = round(max(request.user.accuracy or 0, conf_acc), 1)

        return ok(
            data={
                "image_count": image_count,
                "defect_count": defect_count,
                "accuracy": accuracy,
            }
        )


class DefectTypeStatisticsView(APIView):
    """缺陷类型分布：GET /api/statistics/defect-types/

    返回: {crack: 1050, spalling: 520, ...}
    普通用户只统计自己提交的检测，管理员统计全部。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 历史数据可能有不同命名，统一归一到 BDI 6 类（英文）
        NORMALIZE = {
            "liefeng": "crack",       # 裂缝
            "bolou": "breakage",      # 剥落 -> 破损
            "fengwo": "breakage",     # 蜂窝 -> 破损
            "mamian": "breakage",     # 麻面 -> 破损
            "kongdong": "hole",       # 空洞 -> 孔洞
            "lujin": "reinforcement", # 露筋 -> 钢筋外露
            "shenshui": "seepage",    # 渗水
            "spalling": "breakage",
            "pothole": "hole",
            "corrosion": "other",
        }
        qs = _defects_for_user(request).values("defect_type").annotate(count=Count("id"))
        data = {}
        for item in qs:
            key = NORMALIZE.get(item["defect_type"], item["defect_type"])
            data[key] = data.get(key, 0) + item["count"]
        # 保证所有类型都返回
        for key in ["crack", "breakage", "comb", "hole", "reinforcement", "seepage", "other"]:
            data.setdefault(key, 0)
        return ok(data=data)


class TrendStatisticsView(APIView):
    """近 N 天检测趋势：GET /api/statistics/trend/?days=7"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 7))
        days = max(1, min(days, 90))
        start = timezone.now() - timedelta(days=days - 1)

        rows = (
            _tasks_for_user(request)
            .filter(created_at__gte=start)
            .extra(select={"day": "DATE(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        data = [{"date": str(r["day"]), "count": r["count"]} for r in rows]
        return ok(data=data)
