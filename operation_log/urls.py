from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('operation-logs', views.OperationLogViewSet, basename='operation-log')
router.register('system-logs', views.SystemLogViewSet, basename='system-log')

urlpatterns = [
    path('', include(router.urls)),
]
