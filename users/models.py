"""
用户模型 - 用户注册登录
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField('手机号', max_length=11, unique=True, null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.username
