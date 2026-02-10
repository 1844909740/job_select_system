# Django后端项目 - Python 3.12

完整的Django REST API后端项目，包含8个功能模块。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动服务器
python manage.py runserver
```

## 前端使用

项目包含一个完整的前端界面，位于 `frontend` 目录中。前端使用HTML、CSS和JavaScript开发，使用Bootstrap作为UI框架，Chart.js用于数据可视化。

### 访问前端

1. 启动后端服务器后，打开浏览器
2. 访问 `http://localhost:8000/frontend/index.html`

### 前端功能

- **用户认证**：登录、注册、个人资料管理
- **岗位查询**：支持多条件筛选、收藏岗位
- **数据采集管理**：创建、运行、管理采集任务
- **统计分析**：查看各种统计数据和图表
- **可视化展示**：创建仪表盘和图表组件
- **AI智能分析**：运行各种AI算法并查看分析结果
- **操作日志**：查看系统操作日志和用户行为记录
- **用户管理**：管理用户、角色和权限

## API端点

- `/api/users/` - 用户认证和管理
- `/api/data/` - 数据采集管理
- `/api/position/` - 岗位查询
- `/api/statistics/` - 统计分析
- `/api/visualization/` - 可视化展示
- `/api/logs/` - 操作日志
- `/api/ai/` - AI分析

## 技术栈

- Django 5.0.1 (Python 3.12兼容)
- Django REST Framework
- JWT认证
- MySQL数据库
- Bootstrap 5
- Chart.js
- JavaScript (ES6+)