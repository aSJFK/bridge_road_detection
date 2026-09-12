"""操作日志中间件：记录已认证用户的关键操作"""

import logging

logger = logging.getLogger(__name__)


class OperationLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 跳过文件请求与 admin
        path = request.path
        if path.startswith("/static/") or path.startswith("/media/") or path.startswith("/admin/") or path.startswith("/api/auth/"):
            return self.get_response(request)

        # 仅在写操作时异步记录（避免拖慢请求）
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)

        response = self.get_response(request)

        try:
            user = request.user
            if user and user.is_authenticated:
                from notifications.models import OperationLog

                OperationLog.objects.create(
                    user=user,
                    operation=request.method,
                    module=path.split("/")[2] if len(path.split("/")) > 2 else "api",
                    description=f"{request.method} {path} -> {response.status_code}",
                    ip_address=self._client_ip(request),
                )
        except Exception:  # noqa: BLE001
            logger.warning("操作日志记录失败", exc_info=True)

        return response

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
