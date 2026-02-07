from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('reports', views.StatisticsReportViewSet, basename='statistics-report')
router.register('industry', views.IndustryStatisticsViewSet, basename='industry-statistics')
router.register('salary', views.SalaryStatisticsViewSet, basename='salary-statistics')

urlpatterns = [path('', include(router.urls))]
