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

## API端点

- `/api/users/` - 用户认证
- `/api/data/` - 数据采集
- `/api/position/` - 岗位查询
- `/api/statistics/` - 统计分析
- `/api/visualization/` - 可视化
- `/api/logs/` - 操作日志
- `/api/ai/` - AI分析

## 技术栈

- Django 5.0.1 (Python 3.12兼容)
- Django REST Framework
- JWT认证
- SQLite数据库

