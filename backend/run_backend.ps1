# 桥路缺陷检测系统 - 后端启动脚本（Windows）
# 用法: powershell -ExecutionPolicy Bypass -File run_backend.ps1

Set-Location $PSScriptRoot

# 1. 安装依赖
Write-Host "[1/4] 安装依赖..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

# 2. 初始化数据库（建库 + 迁移）
Write-Host "[2/4] 初始化数据库..." -ForegroundColor Cyan
$env:MYSQL_PWD = "zs20050331"
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS bridge_defect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py migrate

# 3. 初始化示例数据（管理员 admin / admin123456）
Write-Host "[3/4] 初始化示例数据..." -ForegroundColor Cyan
python manage.py init_data

# 4. 启动服务
Write-Host "[4/4] 启动服务 http://127.0.0.1:8000 ..." -ForegroundColor Cyan
python manage.py runserver 0.0.0.0:8000
