"""
用户路由配置
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('permissions', views.PermissionViewSet, basename='permissions')
router.register('roles', views.RoleViewSet, basename='roles')
router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.get_current_user, name='current_user'),
    path('profile/', views.update_user_profile, name='update_profile'),
    # 管理员权限管理
    path('users/<int:user_id>/promote/', views.promote_user, name='promote_user'),
    path('users/<int:user_id>/demote/', views.demote_user, name='demote_user'),
    path('users/<int:user_id>/transfer-superuser/', views.transfer_superuser, name='transfer_superuser'),
    path('', include(router.urls)),
]
