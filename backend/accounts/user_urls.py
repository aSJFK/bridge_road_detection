from django.urls import path
from .views import UserInfoView

urlpatterns = [
    path("info/", UserInfoView.as_view(), name="user-info"),
]
