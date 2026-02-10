"""
用户序列化器
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Permission, Role

User = get_user_model()


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
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次密码不一致")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
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
    """自定义JWT令牌序列化器"""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
