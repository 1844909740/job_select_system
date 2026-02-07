"""
岗位数据查询路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('positions', views.PositionViewSet, basename='position')
router.register('queries', views.PositionQueryViewSet, basename='position-query')
router.register('favorites', views.FavoritePositionViewSet, basename='favorite-position')

urlpatterns = [
    path('', include(router.urls)),
]
