"""
用户视图
"""
import logging
import traceback
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
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
logger = logging.getLogger('users')


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
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            # 将 DRF 的校验错误转换为更友好的格式返回给前端
            # 格式: { "errors": { "username": ["错误信息1"], "email": ["错误信息2"] } }
            logger.warning(
                f'用户注册校验失败: IP={request.META.get("REMOTE_ADDR")}, '
                f'提交数据={{"username": "{request.data.get("username", "")}", '
                f'"email": "{request.data.get("email", "")}", '
                f'"phone": "{request.data.get("phone", "")}"}}, '
                f'错误={serializer.errors}'
            )
            return Response({
                'error': '注册信息校验失败',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            
            # 记录操作日志
            self._log_registration_success(request, user)
            
            logger.info(
                f'用户注册成功: username={user.username}, email={user.email}, '
                f'IP={request.META.get("REMOTE_ADDR")}'
            )
            
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # 非校验类的异常（如数据库错误等）
            logger.error(
                f'用户注册异常: username={request.data.get("username", "")}, '
                f'错误类型={type(e).__name__}, 错误信息={str(e)}, '
                f'IP={request.META.get("REMOTE_ADDR")}\n'
                f'{traceback.format_exc()}'
            )
            self._log_registration_failure(request, str(e))
            
            return Response({
                'error': '注册失败，服务器内部错误，请稍后重试',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _log_registration_success(self, request, user):
        """记录注册成功的操作日志"""
        try:
            from operation_log.models import SystemLog
            SystemLog.objects.create(
                level='INFO',
                message=f'新用户注册成功: {user.username}',
                module='users',
                extra_data={
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
        except Exception as log_err:
            logger.error(f'记录注册成功日志失败: {log_err}')

    def _log_registration_failure(self, request, error_msg):
        """记录注册失败的系统日志"""
        try:
            from operation_log.models import SystemLog
            SystemLog.objects.create(
                level='ERROR',
                message=f'用户注册失败: {error_msg}',
                module='users',
                extra_data={
                    'username': request.data.get('username'),
                    'email': request.data.get('email'),
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
        except Exception as log_err:
            logger.error(f'记录注册失败日志失败: {log_err}')


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，返回用户信息并记录日志"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # 登录成功，记录操作日志
        if response.status_code == 200:
            self._log_login_success(request, response.data.get('user', {}))
        
        return response

    def _log_login_success(self, request, user_data):
        """记录登录成功的操作日志"""
        try:
            username = user_data.get('username', request.data.get('username', ''))
            user_id = user_data.get('id')
            
            from operation_log.models import OperationLog, SystemLog
            
            if user_id:
                OperationLog.objects.create(
                    user_id=user_id,
                    action_type='登录',
                    module='users',
                    description=f'用户 {username} 登录系统',
                    status='成功',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_path=request.path,
                    request_method='POST',
                    response_code=200,
                )
            
            SystemLog.objects.create(
                level='INFO',
                message=f'用户登录成功: {username}',
                module='users',
                extra_data={
                    'user_id': user_id,
                    'username': username,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
        except Exception as e:
            logger.error(f'记录登录日志失败: {e}')

    def handle_exception(self, exc):
        """覆写异常处理，记录登录失败日志"""
        response = super().handle_exception(exc)
        
        username = self.request.data.get('username', '未知')
        logger.warning(
            f'用户登录失败: username={username}, '
            f'IP={self.request.META.get("REMOTE_ADDR")}, '
            f'状态码={response.status_code}'
        )
        
        # 记录到系统日志
        try:
            from operation_log.models import SystemLog
            SystemLog.objects.create(
                level='WARNING',
                message=f'用户登录失败: {username}',
                module='users',
                extra_data={
                    'username': username,
                    'ip_address': self.request.META.get('REMOTE_ADDR'),
                    'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
                    'error': str(exc),
                }
            )
        except Exception as log_err:
            logger.error(f'记录登录失败日志失败: {log_err}')
        
        return response


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
        logger.info(f'用户更新资料: {request.user.username} (ID: {request.user.id})')
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
        target_user = self.get_object()
        
        # 不能删除自己
        if target_user.id == request.user.id:
            return Response({'error': '不能删除自己的账户'}, status=status.HTTP_403_FORBIDDEN)
        
        # 普通管理员不能删除超级管理员
        if target_user.is_superuser and not request.user.is_superuser:
            return Response({'error': '普通管理员无权删除超级管理员'}, status=status.HTTP_403_FORBIDDEN)
        
        # 只有超级管理员可以删除管理员
        if target_user.is_staff and not request.user.is_superuser:
            return Response({'error': '只有超级管理员可以删除管理员账户'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def promote_user(request, user_id):
    """
    超级管理员将普通用户升级为管理员（is_staff=True）
    """
    if not request.user.is_superuser:
        return Response({'error': '只有超级管理员可以执行此操作'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    if target_user.is_staff:
        return Response({'error': f'用户 {target_user.username} 已经是管理员'}, status=status.HTTP_400_BAD_REQUEST)
    
    target_user.is_staff = True
    target_user.save(update_fields=['is_staff'])
    
    logger.info(f'用户 {target_user.username} 被 {request.user.username} 升级为管理员')
    
    # 记录操作日志
    try:
        from operation_log.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action_type='授权',
            module='users',
            description=f'将用户 {target_user.username} 升级为管理员',
            status='成功',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )
    except Exception:
        pass
    
    return Response({
        'message': f'已将用户 {target_user.username} 升级为管理员',
        'user': UserSerializer(target_user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demote_user(request, user_id):
    """
    超级管理员将管理员降级为普通用户（is_staff=False）
    """
    if not request.user.is_superuser:
        return Response({'error': '只有超级管理员可以执行此操作'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    if target_user.is_superuser:
        return Response({'error': '不能降级超级管理员'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not target_user.is_staff:
        return Response({'error': f'用户 {target_user.username} 已经是普通用户'}, status=status.HTTP_400_BAD_REQUEST)
    
    target_user.is_staff = False
    target_user.save(update_fields=['is_staff'])
    
    logger.info(f'用户 {target_user.username} 被 {request.user.username} 降级为普通用户')
    
    try:
        from operation_log.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action_type='取消授权',
            module='users',
            description=f'将管理员 {target_user.username} 降级为普通用户',
            status='成功',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )
    except Exception:
        pass
    
    return Response({
        'message': f'已将管理员 {target_user.username} 降级为普通用户',
        'user': UserSerializer(target_user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_superuser(request, user_id):
    """
    超级管理员将超级管理员权限转让给另一个管理员
    转让后自己仍保留管理员身份（is_staff=True），但不再是超级管理员
    """
    if not request.user.is_superuser:
        return Response({'error': '只有超级管理员可以执行此操作'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    if target_user.id == request.user.id:
        return Response({'error': '不能转让给自己'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not target_user.is_staff:
        return Response({'error': '只能将超级管理员权限转让给管理员，请先将该用户升级为管理员'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 执行转让
    target_user.is_superuser = True
    target_user.save(update_fields=['is_superuser'])
    
    request.user.is_superuser = False
    request.user.save(update_fields=['is_superuser'])
    
    logger.info(f'超级管理员 {request.user.username} 将超级管理员权限转让给 {target_user.username}')
    
    try:
        from operation_log.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action_type='授权',
            module='users',
            description=f'将超级管理员权限转让给 {target_user.username}',
            status='成功',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )
    except Exception:
        pass
    
    return Response({
        'message': f'已将超级管理员权限转让给 {target_user.username}',
        'user': UserSerializer(target_user).data,
    })
