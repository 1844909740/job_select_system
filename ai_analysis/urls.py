from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('algorithms', views.AIAlgorithmViewSet, basename='ai-algorithm')
router.register('tasks', views.AIAnalysisTaskViewSet, basename='ai-task')

urlpatterns = [
    path('analyze-resume/', views.analyze_resume, name='analyze-resume'),
    path('', include(router.urls)),
]
