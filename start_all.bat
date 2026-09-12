@echo off
REM ====================================================
REM  桥路缺陷检测系统 - 一键启动脚本
REM  同时启动 后端(Django:8000) 和 前端(Vite:5173)
REM ====================================================
title 桥路缺陷检测系统 - 启动器

echo.
echo  [1/2] 启动后端 Django (http://127.0.0.1:8000) ...
cd /d E:\bridge_road_detection\detection_web\backend
start "django-backend" D:\anaconda3\envs\torch\python.exe manage.py runserver 0.0.0.0:8000 --noreload

echo  [2/2] 启动前端 Vite  (http://127.0.0.1:5173) ...
cd /d E:\bridge_road_detection\detection_web\frontend
start "frontend-vite" cmd /k npm run dev -- --host 127.0.0.1 --port 5173

echo.
echo  ====================================================
echo   启动完成！请在浏览器打开:  http://127.0.0.1:5173
echo   管理员账号: admin / admin123456
echo  ====================================================
timeout /t 5 >nul
