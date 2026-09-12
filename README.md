# 桥路缺陷检测系统（Bridge & Road Defect Detection System）

基于 **YOLOv8 双模型**（桥梁 + 公路）的桥梁与道路表面缺陷智能检测平台。

- 前端：Vue 3 + Vite + TypeScript + Element Plus + ECharts
- 后端：Django 5 + Django REST Framework + JWT
- 数据库：MySQL 8.0
- 检测：YOLOv8 双模型，上传图片自动检测并生成报告

## 功能

- 用户登录 / 注册（管理员账号固定，普通用户可注册）
- 单图检测：上传图片 → 桥梁/公路双模型分别检测 → 融合标注 → 自动生成报告
- 报告管理：查看报告详情、缺陷明细、下载 HTML 报告
- 报告评价：用户对报告打分评论（提交后不可修改，管理员可删改）
- 数据统计：首页统计、缺陷类型分布、检测趋势
- 缺陷管理 / 数据集管理（数据集为占位）

---

## 快速开始（本地复现）

### 前置要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+（需含 MySQL 驱动） |
| Node.js | 18+ |
| MySQL | 8.0 |

### 第 1 步：克隆项目

```bash
git clone <你的仓库地址>
cd detection_web
```

### 第 2 步：初始化 MySQL

创建数据库（字符集 utf8mb4）：

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS bridge_defect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 第 3 步：配置数据库连接

```bash
cd backend
copy .env.example .env    # Windows
# 或
cp .env.example .env      # macOS / Linux
```

编辑 `.env`，把 `DB_PASSWORD` 改成你自己的 MySQL 密码。

### 第 4 步：安装后端依赖

```bash
pip install -r requirements.txt
```

> 如遇 `mysqlclient` 安装失败，可改用 `PyMySQL`：`pip install PyMySQL` 并在 `config/settings.py` 的 `DATABASES` 前加 `import pymysql; pymysql.install_as_MySQLdb()`。

### 第 5 步：迁移 + 初始化数据

```bash
python manage.py migrate
python manage.py init_data
```

`init_data` 会创建：
- 管理员 `admin` / `admin123456`（固定）
- 普通用户 `testuser` / `user123456`
- 示例检测任务、缺陷、数据集、通知

### 第 6 步：放置 YOLO 模型（可选）

把训练好的模型放到 `backend/models/` 目录：

```
backend/models/bridge.pt   # 桥梁模型
backend/models/road.pt     # 公路模型
```

> 模型文件使用自定义 `CBAM` 模块，需把 `ultralytics/nn/CBAM.py` 放入你的 ultralytics 安装目录（`site-packages/ultralytics/nn/`）。
> 模型缺失时接口会返回明确错误（不使用模拟数据）。

### 第 7 步：启动后端

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

验证：浏览器打开 http://127.0.0.1:8000/api/home/statistics/ 应返回 JSON。

### 第 8 步：启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://127.0.0.1:5173 ，用 `admin / admin123456` 登录。

---

## 目录结构

```
detection_web/
├── backend/            # Django 后端
│   ├── config/         # 项目配置（settings/urls）
│   ├── accounts/       # 用户认证
│   ├── detection/      # 检测任务 + YOLO 服务
│   ├── defects/        # 缺陷管理
│   ├── reports/        # 报告 + 评价
│   ├── datasets/       # 数据集（占位）
│   ├── statistics_app/ # 统计接口
│   ├── notifications/  # 通知 + 操作日志
│   ├── scripts/        # 数据初始化命令
│   └── models/         # YOLO 模型文件（不入库，自行放置）
└── frontend/           # Vue 3 前端
    └── src/
        ├── api/        # API 客户端
        ├── views/      # 页面
        └── components/ # 组件
```

## 核心 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login/ | 登录（JWT） |
| POST | /api/auth/register/ | 注册（普通用户） |
| GET | /api/user/info/ | 当前用户信息 |
| POST | /api/detection/tasks/ | 上传图片检测（自动生成报告） |
| GET | /api/detection/recent/ | 最近检测记录 |
| GET | /api/reports/ | 报告列表 |
| GET | /api/reports/{id}/ | 报告详情 |
| POST | /api/reports/{id}/rate/ | 提交评价 |
| GET | /api/home/statistics/ | 首页统计 |

## 权限

- **管理员**：全部权限（含系统管理）
- **普通用户**：上传检测、查看/评价自己的报告

## 注意事项

- 前端通过 Vite 代理将 `/api` 和 `/media` 转发到后端 8000 端口
- `.env`、模型文件、数据库文件均被 git 忽略，不会提交
