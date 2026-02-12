"""
用户序列化器
"""
import re
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Permission, Role

User = get_user_model()
logger = logging.getLogger('users')


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ['created_at']


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source='permissions'
    )
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器 - 包含完整的字段校验"""
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=32,
        error_messages={
            'min_length': '密码长度不能少于6位',
            'max_length': '密码长度不能超过32位',
            'required': '请输入密码',
            'blank': '密码不能为空',
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '请输入确认密码',
            'blank': '确认密码不能为空',
        }
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        extra_kwargs = {
            'username': {
                'min_length': 3,
                'max_length': 20,
                'error_messages': {
                    'min_length': '用户名长度不能少于3个字符',
                    'max_length': '用户名长度不能超过20个字符',
                    'required': '请输入用户名',
                    'blank': '用户名不能为空',
                }
            },
            'email': {
                'error_messages': {
                    'required': '请输入邮箱地址',
                    'blank': '邮箱不能为空',
                    'invalid': '邮箱格式不正确，请输入有效的邮箱地址',
                }
            },
            'phone': {
                'error_messages': {
                    'required': '请输入手机号',
                    'blank': '手机号不能为空',
                }
            },
        }

    def validate_username(self, value):
        """校验用户名格式和唯一性"""
        # 格式校验：只允许字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', value):
            raise serializers.ValidationError('用户名只能包含字母、数字、下划线和中文')
        # 唯一性校验
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已被注册，请换一个')
        return value

    def validate_email(self, value):
        """校验邮箱唯一性"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册，请使用其他邮箱或直接登录')
        return value

    def validate_phone(self, value):
        """校验手机号格式和唯一性"""
        if not value:
            raise serializers.ValidationError('手机号不能为空')
        # 中国大陆手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确，请输入11位有效手机号')
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已被注册')
        return value

    def validate_password(self, value):
        """校验密码强度"""
        if value.isdigit():
            raise serializers.ValidationError('密码不能是纯数字，请包含字母')
        if value.isalpha():
            raise serializers.ValidationError('密码不能是纯字母，请包含数字')
        return value

    def validate(self, attrs):
        """校验两次密码是否一致"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')

        # 首个注册的用户自动成为超级管理员
        is_first_user = not User.objects.exists()

        user = User.objects.create_user(**validated_data)

        if is_first_user:
            user.is_superuser = True
            user.is_staff = True
            user.save(update_fields=['is_superuser', 'is_staff'])
            logger.info(f'系统首个用户注册，自动设为超级管理员: {user.username} (ID: {user.id})')
        else:
            logger.info(f'新用户注册成功: {user.username} (ID: {user.id}, Email: {user.email})')

        return user


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        source='role',
        required=False
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'role', 'role_id', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'created_at']
        read_only_fields = ['id', 'is_superuser', 'is_staff', 'date_joined', 'created_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义JWT令牌序列化器 - 增加登录日志"""

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data['user'] = UserSerializer(self.user).data
            logger.info(
                f'用户登录成功: {self.user.username} (ID: {self.user.id})'
            )
            return data
        except Exception as e:
            # 记录登录失败日志（用户名可能存在也可能不存在）
            username = attrs.get('username', '未知')
            logger.warning(f'用户登录失败: 用户名={username}, 原因={str(e)}')
            raise

    default_error_messages = {
        'no_active_account': '用户名或密码错误，请重新输入'
    }
