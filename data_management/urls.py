"""
数据采集管理路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('sources', views.DataSourceViewSet, basename='data-source')
router.register('tasks', views.DataTaskViewSet, basename='data-task')
router.register('records', views.DataRecordViewSet, basename='data-record')

urlpatterns = [
    path('', include(router.urls)),
]
