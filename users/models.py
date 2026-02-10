"""
用户模型 - 用户注册登录
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    """权限模型"""
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限代码', max_length=100, unique=True)
    description = models.TextField('权限描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'permissions'
        verbose_name = '权限'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class Role(models.Model):
    """角色模型"""
    name = models.CharField('角色名称', max_length=100, unique=True)
    description = models.TextField('角色描述', blank=True)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField('手机号', max_length=11, unique=True, null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.username
    
    def has_permission(self, permission_code):
        """检查用户是否有指定权限"""
        if not self.role:
            return False
        return self.role.permissions.filter(code=permission_code).exists()
    
    def has_any_permission(self, permission_codes):
        """检查用户是否有任意指定权限"""
        if not self.role:
            return False
        return self.role.permissions.filter(code__in=permission_codes).exists()
    
    def has_all_permissions(self, permission_codes):
        """检查用户是否有所有指定权限"""
        if not self.role:
            return False
        return self.role.permissions.filter(code__in=permission_codes).count() == len(permission_codes)
