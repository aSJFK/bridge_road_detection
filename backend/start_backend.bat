@echo off
cd /d E:\bridge_road_detection\detection_web\backend
start "django-backend" /b D:\anaconda3\envs\torch\python.exe manage.py runserver 0.0.0.0:8000 --noreload
