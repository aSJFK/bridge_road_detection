from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "avatar", "is_active", "date_joined", "accuracy"]
        read_only_fields = ["id", "date_joined", "accuracy"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=128)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone"]
        extra_kwargs = {
            "username": {"required": True, "min_length": 3},
            "role": {"required": False},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value

    def validate(self, attrs):
        # 公开注册不允许指定任意角色，统一为普通用户，防止越权
        attrs["role"] = "user"
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Django 加密保存
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """登录返回 access/refresh + 用户信息"""

    def validate(self, attrs):
        data = super().validate(attrs)
        # 首次登录：初始化准确率为 90~95 之间的随机值
        if not self.user.accuracy:
            import random

            self.user.accuracy = round(random.uniform(90.0, 95.0), 1)
            self.user.save(update_fields=["accuracy"])
        data["user"] = UserInfoSerializer(self.user).data
        return data
