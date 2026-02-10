"""
用户视图
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PermissionSerializer,
    RoleSerializer
)
from .models import Permission, Role

User = get_user_model()


def has_permission(permission_code):
    """自定义权限检查装饰器"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
            if not request.user.has_permission(permission_code):
                return Response({'error': '无权限执行此操作'}, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class UserRegistrationView(generics.CreateAPIView):
    """用户注册"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 记录异常信息
            from operation_log.models import SystemLog
            SystemLog.objects.create(
                level='ERROR',
                message=f'用户注册失败: {str(e)}',
                module='users',
                extra_data={
                    'username': request.data.get('username'),
                    'email': request.data.get('email'),
                    'ip_address': request.META.get('REMOTE_ADDR')
                }
            )
            return Response({
                'error': '注册失败',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，返回用户信息"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前登录用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """更新用户信息"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionViewSet(viewsets.ModelViewSet):
    """权限管理视图集"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    @has_permission('permission_manage')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @has_permission('permission_manage')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @has_permission('permission_manage')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    @has_permission('role_manage')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @has_permission('role_manage')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @has_permission('role_manage')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @has_permission('user_manage')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @has_permission('user_manage')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @has_permission('user_manage')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
