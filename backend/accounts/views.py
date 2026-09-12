from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from common.responses import ok, fail
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserInfoSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    """登录：POST /api/auth/login/  body: {username, password}"""

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """注册：POST /api/auth/register/  body: {username, email, password, phone}"""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return ok(
            data={
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
            message="注册成功",
            code=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """退出登录：POST /api/auth/logout/  body: {refresh}（将 refresh 拉黑）"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        return ok(data=None, message="已退出登录")


class UserInfoView(APIView):
    """用户信息：GET /api/user/info/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok(data=UserInfoSerializer(request.user).data)
