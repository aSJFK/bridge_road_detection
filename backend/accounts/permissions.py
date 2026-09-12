from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """仅管理员"""

    message = "需要管理员权限"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")
