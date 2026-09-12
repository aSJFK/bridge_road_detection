"""桥路缺陷检测系统 - Django 配置"""
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-bridge-defect-detection-system-change-me"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---- 应用 ----
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 第三方
    "rest_framework",
    "corsheaders",
    # 业务
    "accounts",
    "detection",
    "defects",
    "datasets",
    "reports",
    "notifications",
    "common",
    "scripts",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.OperationLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---- MySQL 8.0 ----
# 优先从环境变量读取，便于其他人克隆后用自己的 MySQL 密码
# 也可在 backend/.env 中配置（格式：DB_PASSWORD=你的密码）
import os


def _load_dotenv(path):
    """简易 .env 加载"""
    try:
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except Exception:
        pass


_load_dotenv(BASE_DIR / ".env")

DB_NAME = os.environ.get("DB_NAME", "bridge_defect_db")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "zs20050331")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ---- 缓存 ----
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ---- 密码 ----
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
]

AUTH_USER_MODEL = "accounts.User"

# ---- DRF + JWT ----
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "EXCEPTION_HANDLER": "common.responses.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
}

# ---- 跨域 ----
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境放开；正式环境由 Nginx 处理

# ---- 国际化 ----
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = False

# ---- 静态/媒体 ----
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 统一上传大小限制：10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ---- YOLO 模型配置（双模型：桥梁 / 公路） ----
# 每个模型独立：pt 文件存在则使用真实 YOLOv8 推理，缺失则报错
YOLO_BRIDGE_MODEL_PATH = BASE_DIR / "models" / "bridge.pt"
YOLO_ROAD_MODEL_PATH = BASE_DIR / "models" / "road.pt"
YOLO_CONF_THRESHOLD = 0.25
YOLO_IMG_SIZE = 640

# BDI 配套的修改版 ultralytics（模型依赖其自定义模块，如 DFLoss/C3k2）
# 加载模型前会优先把该目录加入 sys.path
# 优先用环境变量（便于部署到其他目录），否则用相对默认路径
ULTRAYLITICS_RUNTIME = (
    Path(os.environ["ULTRAYLITICS_RUNTIME"])
    if os.environ.get("ULTRAYLITICS_RUNTIME")
    else BASE_DIR.parents[1] / "BDI-main" / "backend" / "external_runtimes" / "prnet_ultralytics"
)

# 缺陷类型 -> 中文名/颜色映射（用于结果图片绘制）
# BDI 6 类模型类别（Crack/Breakage/Comb/Hole/Reinforcement/Seepage）
DEFECT_META = {
    "crack": {"label": "裂缝", "color": (30, 144, 255)},
    "breakage": {"label": "破损", "color": (255, 165, 61)},
    "comb": {"label": "梳齿缺陷", "color": (47, 214, 214)},
    "hole": {"label": "孔洞", "color": (240, 87, 74)},
    "reinforcement": {"label": "钢筋外露", "color": (144, 100, 250)},
    "seepage": {"label": "渗水", "color": (100, 180, 220)},
    # 兼容旧中文拼音类别
    "liefeng": {"label": "裂缝", "color": (30, 144, 255)},
    "bolou": {"label": "剥落", "color": (255, 165, 61)},
    "fengwo": {"label": "蜂窝", "color": (47, 214, 214)},
    "mamian": {"label": "麻面", "color": (124, 127, 220)},
    "kongdong": {"label": "空洞", "color": (240, 87, 74)},
    "lujin": {"label": "露筋", "color": (144, 100, 250)},
    "shenshui": {"label": "渗水", "color": (100, 180, 220)},
    "spalling": {"label": "剥落", "color": (255, 165, 61)},
    "pothole": {"label": "坑洞", "color": (47, 214, 214)},
    "corrosion": {"label": "钢筋锈蚀", "color": (240, 87, 74)},
    "other": {"label": "其他", "color": (124, 127, 220)},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
