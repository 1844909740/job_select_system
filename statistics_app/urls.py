"""
统计分析路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('reports', views.StatisticsReportViewSet, basename='statistics-report')
router.register('industry', views.IndustryStatisticsViewSet, basename='industry-statistics')
router.register('salary', views.SalaryStatisticsViewSet, basename='salary-statistics')

urlpatterns = [
    path('basic/', views.basic_statistics, name='basic-statistics'),
    path('salary-distribution/', views.salary_distribution, name='salary-distribution'),
    path('experience-distribution/', views.experience_distribution, name='experience-distribution'),
    path('education-distribution/', views.education_distribution, name='education-distribution'),
    path('position-type-distribution/', views.position_type_distribution, name='position-type-distribution'),
    path('city-distribution/', views.city_distribution, name='city-distribution'),
    path('industry-distribution/', views.industry_distribution, name='industry-distribution'),
    path('company-distribution/', views.company_distribution, name='company-distribution'),
    path('', include(router.urls)),
]
