# 岗位智能分析系统 (AI Job Select System)

基于 Django REST Framework + React (Vite) 的全栈岗位数据分析系统，包含 8 个功能模块。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 4.2.7 + Django REST Framework 3.14 |
| 认证方式 | JWT（djangorestframework-simplejwt） |
| 数据库 | MySQL 8.0+（通过 PyMySQL 连接） |
| 前端框架 | React 18 + Vite 5 |
| UI 组件库 | Ant Design 5 |
| 数据可视化 | ECharts 5（echarts-for-react） |
| 状态管理 | Zustand |
| HTTP 客户端 | Axios |
| Python 版本 | Python 3.12 |

## 环境准备（前置要求）

在开始之前，请确保你的电脑已安装以下软件：

- **Python 3.12**（[下载地址](https://www.python.org/downloads/)）
- **Node.js 18+**（[下载地址](https://nodejs.org/)，安装后自带 npm）
- **MySQL 8.0+**（[下载地址](https://dev.mysql.com/downloads/mysql/)）
- **Git**（[下载地址](https://git-scm.com/downloads)）

## 快速开始

> 以下所有命令中，**项目根目录** 指的是 `job_select_system/` 文件夹（即包含 `manage.py` 的目录）。

### 第一步：克隆项目

```bash
git clone <你的仓库地址>
cd job_select_system
```

### 第二步：创建并激活 Python 虚拟环境

在 **项目根目录**（`job_select_system/`）下执行：
1.创建一个.venv文件夹
2.点击右上角的Settings
3.找到Python Interpreter点击使用python3.12版本

激活成功后，终端提示符前会出现 `(venv)` 标识。

### 第三步：安装 Python 后端依赖

在 **项目根目录**（`job_select_system/`）下，确认虚拟环境已激活后执行：

```bash
pip install -r requirements.txt
```

### 第四步：创建 MySQL 数据库

打开 MySQL 命令行客户端（或使用 Navicat、DBeaver 等工具），执行以下 SQL：

```sql
CREATE DATABASE django_job_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 第五步：配置数据库连接

编辑 `backend/settings.py` 文件中的 `DATABASES` 配置，修改为你本机的 MySQL 用户名和密码：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_job_system',      # 数据库名（第四步创建的）
        'USER': 'root',                    # 你的 MySQL 用户名
        'PASSWORD': '123456789',           # 你的 MySQL 密码
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### 第六步：执行数据库迁移

在 **项目根目录**（`job_select_system/`）下执行：

```bash
python manage.py makemigrations
python manage.py migrate
```

### 第七步：创建超级管理员账号

在 **项目根目录**（`job_select_system/`）下执行：

```bash
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 第八步：启动 Django 后端服务器

在 **项目根目录**（`job_select_system/`）下执行：

```bash
python manage.py runserver
```

后端服务将运行在 `http://localhost:8000`。

### 第九步：安装前端依赖

**新开一个终端窗口**，进入 **前端目录**（`job_select_system/frontend/`）：

```bash
cd frontend
npm install
```

### 第十步：启动前端开发服务器

在 **前端目录**（`job_select_system/frontend/`）下执行：

```bash
npm run dev
```

前端开发服务器将运行在 `http://localhost:3000`，并自动将 `/api` 请求代理到后端 `http://localhost:8000`。

### 第十一步：访问系统

打开浏览器，访问 **`http://localhost:3000`**，即可使用系统。

- 前端界面：`http://localhost:3000`
- 后端 API：`http://localhost:8000/api/`
- Django 管理后台：`http://localhost:8000/admin/`

## 目录结构

```
job_select_system/                # 项目根目录
├── manage.py                     # Django 管理脚本
├── requirements.txt              # Python 依赖清单
├── README.md
├── backend/                      # Django 项目配置
│   ├── settings.py               # 项目设置（数据库、中间件等）
│   ├── urls.py                   # 根路由配置
│   ├── middleware.py              # 自定义中间件
│   ├── wsgi.py
│   └── asgi.py
├── users/                        # 用户认证与管理模块
├── data_management/              # 数据采集管理模块
├── position_data/                # 岗位数据模块
├── statistics_app/               # 统计分析模块
├── visualization/                # 可视化展示模块
├── operation_log/                # 操作日志模块
├── ai_analysis/                  # AI 智能分析模块
└── frontend/                     # React 前端项目
    ├── package.json              # 前端依赖清单
    ├── vite.config.js            # Vite 配置（含 API 代理）
    ├── index.html                # 入口 HTML
    └── src/                      # 前端源代码
        ├── main.jsx              # React 入口
        ├── App.jsx               # 根组件与路由
        ├── api/                  # API 请求封装
        ├── components/           # 公共组件
        ├── pages/                # 页面组件
        ├── store/                # Zustand 状态管理
        └── styles/               # 全局样式
```

## API 端点

| 路径前缀 | 模块 | 说明 |
|----------|------|------|
| `/api/users/` | 用户模块 | 登录、注册、用户管理、角色权限 |
| `/api/data/` | 数据采集 | 数据源、采集任务、采集记录 |
| `/api/position/` | 岗位查询 | 岗位列表、搜索、收藏 |
| `/api/statistics/` | 统计分析 | 薪资分布、学历分布、城市分布等 |
| `/api/visualization/` | 可视化 | 仪表盘、图表管理 |
| `/api/logs/` | 操作日志 | 操作日志、系统日志 |
| `/api/ai/` | AI 分析 | 算法管理、分析任务、简历分析 |

## 前端功能

- **用户认证**：登录、注册、个人资料管理
- **岗位查询**：支持多条件筛选、收藏岗位
- **数据采集管理**：创建、运行、管理采集任务
- **统计分析**：查看各种统计数据和图表
- **可视化展示**：创建仪表盘和图表组件
- **AI 智能分析**：运行各种 AI 算法并查看分析结果
- **操作日志**：查看系统操作日志和用户行为记录
- **用户管理**：管理用户、角色和权限

## 常见问题

### Q: PowerShell 无法激活虚拟环境？

运行以下命令后重试：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: `pip install` 报错找不到 MySQL 相关包？

本项目使用 `pymysql` 而非 `mysqlclient`，不需要额外安装 MySQL C 开发库。如果仍有问题，确认虚拟环境已正确激活（终端前缀有 `(venv)`）。

### Q: 数据库连接失败？

1. 确认 MySQL 服务正在运行
2. 确认 `backend/settings.py` 中的数据库用户名和密码正确
3. 确认已创建 `django_job_system` 数据库

### Q: 前端页面空白或报网络错误？

确认 Django 后端服务器已在 `http://localhost:8000` 上运行，前端的 API 代理依赖后端服务。

### Q: 如何生成测试岗位数据？

在项目根目录下执行：

```bash
python manage.py generate_data
```
