# 桥路缺陷检测系统 - 后端

Django 5 + DRF + JWT + MySQL 8.0 + YOLOv8 双模型

## 技术栈

- Python 3.11+
- Django 5 / Django REST Framework
- MySQL 8.0（utf8mb4）
- JWT 认证（simplejwt）
- YOLOv8 双模型（桥梁 bridge / 公路 road）

> 完整部署/复现步骤见仓库根目录 `README.md`。

## 快速启动

### 1. 配置数据库

复制 `.env.example` 为 `.env`，修改 `DB_PASSWORD` 为你的 MySQL 密码。

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux
```

创建数据库：

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS bridge_defect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 安装依赖 + 迁移 + 初始化

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py init_data
```

初始化账号：
- 管理员 `admin` / `admin123456`
- 普通用户 `testuser` / `user123456`

### 3. 放置 YOLO 模型（可选）

把模型放到 `backend/models/`：
- `bridge.pt`（桥梁模型）
- `road.pt`（公路模型）

模型使用自定义 CBAM 模块，需将 `ultralytics/nn/CBAM.py` 放入你的 ultralytics 包目录。模型缺失时接口返回明确错误。

### 4. 启动

```bash
python manage.py runserver 0.0.0.0:8000
```

## 核心接口

- `POST /api/auth/login/` 登录
- `POST /api/auth/register/` 注册（普通用户）
- `POST /api/detection/tasks/` 上传图片检测，自动生成报告
- `GET /api/reports/` 报告列表
- `POST /api/reports/{id}/rate/` 提交评价

## 角色

- 管理员 admin：全部权限（含系统管理）
- 普通用户 user：上传检测、查看/评价自己的报告
