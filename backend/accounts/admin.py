from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("额外信息", {"fields": ("role", "avatar", "phone")}),
    )
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
