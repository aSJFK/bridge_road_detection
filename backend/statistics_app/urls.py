from django.urls import path
from .views import DefectTypeStatisticsView, HomeStatisticsView, TrendStatisticsView

urlpatterns = [
    path("home/statistics/", HomeStatisticsView.as_view(), name="home-statistics"),
    path("statistics/defect-types/", DefectTypeStatisticsView.as_view(), name="defect-types"),
    path("statistics/trend/", TrendStatisticsView.as_view(), name="statistics-trend"),
]
