import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from common.responses import ok, fail
from common.viewsets import ApiModelViewSet
from reports.models import InspectionReport
from .services import DetectionService, ModelNotFoundError
from .annotate import annotate, save_result_image
from .report_builder import save_report_file
from .models import DetectionImage, DetectionTask
from .serializers import (
    DetectionImageSerializer,
    DetectionTaskDetailSerializer,
    DetectionTaskListSerializer,
)

logger = logging.getLogger(__name__)


class DetectionTaskViewSet(ApiModelViewSet):
    """检测任务"""

    queryset = DetectionTask.objects.select_related("created_by").prefetch_related("images__defects").all()
    serializer_class = DetectionTaskListSerializer
    search_fields = ["task_name"]
    ordering_fields = ["created_at", "completed_at", "defect_count"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DetectionTaskDetailSerializer
        return DetectionTaskListSerializer

    def get_permissions(self):
        # 上传图片检测对所有登录用户开放（普通用户也能上传）
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # 普通用户只能看自己的任务
        if user.role == "user":
            qs = qs.filter(created_by=user)
        return qs

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """最近检测：GET /api/detection/recent/"""
        qs = self.get_queryset()[:10]
        return ok(
            data=[
                {
                    "id": t.id,
                    "task_name": t.task_name,
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "",
                    "image_count": t.image_count,
                    "defect_count": t.defect_count,
                    "status": t.status,
                    "status_text": t.get_status_display(),
                }
                for t in qs
            ]
        )

    def create(self, request, *args, **kwargs):
        """创建检测任务：POST /api/detection/tasks/  multipart/form-data

        支持：
          - task_name（可选）
          - files / image：一个或多个图片文件
        直接完成检测并保存缺陷与结果图。
        """
        task_name = request.data.get("task_name") or "通用检测"

        files = request.FILES.getlist("files") or request.FILES.getlist("image")
        if not files:
            files = [request.FILES["image"]] if "image" in request.FILES else []
        if not files:
            return fail("请上传图片", 400)

        try:
            with transaction.atomic():
                task = DetectionTask.objects.create(
                    task_name=task_name,
                    status="running",
                    started_at=timezone.now(),
                    created_by=request.user,
                )
                total_defects = 0
                confs = []
                images_payload = []
                report_ids = []

                for f in files:
                    img = self._process_image(task, f, request.user)
                    images_payload.append(DetectionImageSerializer(img).data)
                    total_defects += img.defects.count()
                    confs.extend(d.confidence for d in img.defects.all())
                    # 每张图片自动生成一份检测报告（含可下载的 HTML 文件）
                    defects_qs = img.defects.all()
                    report = InspectionReport.objects.create(
                        task=task,
                        image=img,
                        report_name=f"检测报告-{img.id:05d}",
                        total_images=1,
                        total_defects=img.defects.count(),
                        accuracy=round(sum(d.confidence for d in defects_qs) / defects_qs.count(), 3)
                        if defects_qs.exists()
                        else 0.0,
                        created_by=request.user,
                    )
                    file_rel = f"reports/report_{report.id:05d}.html"
                    save_report_file(report, img, list(defects_qs), file_rel)
                    report.report_file = file_rel
                    report.save(update_fields=["report_file"])
                    report_ids.append(report.id)

                task.image_count = task.images.count()
                task.defect_count = total_defects
                task.accuracy = round(sum(confs) / len(confs), 3) if confs else 0.0
                task.status = "completed"
                task.completed_at = timezone.now()
                task.save()
        except ModelNotFoundError as e:
            return fail(str(e), 400)
        except ValueError as e:
            return fail(str(e), 400)
        except Exception as e:
            logger.exception("检测任务处理失败")
            return fail(f"检测失败: {e}", 500)

        return ok(
            data={
                "task": DetectionTaskDetailSerializer(task).data,
                "images": images_payload,
                "total_defects": total_defects,
                "accuracy": task.accuracy,
                "report_ids": report_ids,
            },
            message="检测完成，已生成报告",
        )

    def _process_image(self, task, file, user) -> DetectionImage:
        """处理单张图片：保存原图 → 双模型检测 → 融合画框 → 保存结果图 → 存缺陷"""
        try:
            pil_image = PILImage.open(file)
            pil_image.load()
        except Exception:
            raise ValueError(f"无法解析图片: {file.name}")

        width, height = pil_image.size

        # 双模型检测（bridge + road，返回带 source 的融合结果，归一化坐标）
        predictions = DetectionService.predict_all(pil_image)

        # 绘制融合结果图
        result_name = f"result_{task.id}_{datetime.now().strftime('%H%M%S%f')}.jpg"
        result_rel = f"detection/result/{result_name}"
        result_path = settings.MEDIA_ROOT / result_rel
        result_path.parent.mkdir(parents=True, exist_ok=True)
        annotated = annotate(pil_image.convert("RGB"), [p.to_dict() for p in predictions])
        save_result_image(annotated, result_path)

        img = DetectionImage.objects.create(
            task=task,
            original_image=file,
            result_image=result_rel,
            image_width=width,
            image_height=height,
            created_by=user,
        )

        for p in predictions:
            d = p.to_dict()
            x1, y1, x2, y2 = d["bbox"]
            img.defects.create(
                defect_type=d["type"],
                source=d["source"],
                confidence=d["confidence"],
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                area=d["area"],
            )
        return img


class PredictView(APIView):
    """图片检测（不落库）：POST /api/detection/predict/  multipart/form-data"""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return fail("缺少 image 参数", 400)
        try:
            pil_image = PILImage.open(image_file)
            pil_image.load()
        except Exception:
            return fail("无法解析图片", 400)

        try:
            predictions = DetectionService.predict_all(pil_image)
        except ModelNotFoundError as e:
            return fail(str(e), 400)
        except Exception as e:
            logger.exception("单图检测失败")
            return fail(f"检测失败: {e}", 500)
        return ok(
            data={
                "count": len(predictions),
                "objects": [p.to_dict() for p in predictions],
            },
            message="检测完成",
        )
