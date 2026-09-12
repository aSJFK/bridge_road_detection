"""检测服务层：View → Service → YOLO Model 分层

双模型设计：
  - 桥梁模型（bridge）与公路模型（road）分别对输入图像做检测
  - 模型 pt 文件必须存在，缺失时直接抛错（不使用 Mock 模拟）
  - 两个模型的预测结果统一返回，带 source 字段，供上层融合画框
"""
import logging
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_SOURCES = ("bridge", "road")


class ModelNotFoundError(Exception):
    """模型文件不存在"""


@dataclass
class Prediction:
    type: str
    confidence: float
    bbox: list  # [x1, y1, x2, y2] 归一化 0~1
    area: float
    source: str = "bridge"  # bridge / road

    def to_dict(self):
        return {
            "type": self.type,
            "confidence": round(self.confidence, 3),
            "bbox": self.bbox,
            "area": round(self.area, 4),
            "source": self.source,
        }


class YOLODetector:
    """真实 YOLOv8 检测器"""

    source = "bridge"

    def __init__(self, source, model_path=None, conf=None, imgsz=None):
        self.source = source
        self.model_path = str(model_path or self._default_path(source))
        self.conf = conf or settings.YOLO_CONF_THRESHOLD
        self.imgsz = imgsz or settings.YOLO_IMG_SIZE
        self._model = None

    @staticmethod
    def _default_path(source: str) -> Path:
        key = f"YOLO_{source.upper()}_MODEL_PATH"
        return getattr(settings, key, settings.BASE_DIR / "models" / f"{source}.pt")

    def _check_available(self):
        if not Path(self.model_path).exists():
            raise ModelNotFoundError(f"未找到 {self.source} 模型文件: {self.model_path}")

    def _load(self):
        if self._model is None:
            import sys

            # 优先使用 BDI 配套的修改版 ultralytics（模型依赖其自定义模块）
            runtime = getattr(settings, "ULTRAYLITICS_RUNTIME", None)
            if runtime and Path(runtime).exists() and str(runtime) not in sys.path:
                sys.path.insert(0, str(runtime))
                logger.info("使用 BDI 配套 ultralytics: %s", runtime)

            from ultralytics import YOLO

            self._check_available()
            logger.info("加载 %s 模型: %s", self.source, self.model_path)
            self._model = YOLO(self.model_path)

    def predict(self, image):
        self._load()
        results = self._model.predict(
            source=image,
            conf=self.conf,
            imgsz=self.imgsz,
            verbose=False,
        )
        predictions = []
        if not results:
            return predictions

        import numpy as np

        img = np.asarray(image.convert("RGB"))
        img_h, img_w = img.shape[0], img.shape[1]
        if img_w <= 0 or img_h <= 0:
            img_w, img_h = self.imgsz, self.imgsz

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            x1, y1, x2, y2 = (
                max(0.0, x1 / img_w),
                max(0.0, y1 / img_h),
                min(1.0, x2 / img_w),
                min(1.0, y2 / img_h),
            )
            label = results[0].names[cls_id] if results[0].names else "other"
            label = label.lower()
            if label not in settings.DEFECT_META:
                label = "other"
            predictions.append(
                Prediction(
                    type=label,
                    confidence=conf,
                    bbox=[round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)],
                    area=round((x2 - x1) * (y2 - y1), 4),
                    source=self.source,
                )
            )
        return predictions


class DetectionService:
    """检测服务：统一入口，管理双模型（bridge / road）"""

    _detectors: dict[str, YOLODetector] = {}

    @classmethod
    def get_detector(cls, source: str) -> YOLODetector:
        if source not in MODEL_SOURCES:
            source = "bridge"
        if source not in cls._detectors:
            cls._detectors[source] = YOLODetector(source)
        return cls._detectors[source]

    @classmethod
    def predict_all(cls, image, sources=None) -> list[Prediction]:
        """双模型分别检测，返回融合结果（带 source）

        某个模型文件缺失时跳过该模型，用存在的模型检测（不报错、不 mock）。
        """
        sources = sources or MODEL_SOURCES
        fused: list[Prediction] = []
        for source in sources:
            try:
                fused.extend(cls.get_detector(source).predict(image))
            except ModelNotFoundError:
                # 模型文件缺失：跳过该模型，不影响其他模型
                logger.warning("%s 模型文件缺失，跳过检测", source)
                continue
            except Exception:
                logger.exception("%s 模型检测失败", source)
                raise
        return fused

    @classmethod
    def reset(cls):
        cls._detectors = {}
