from rest_framework import serializers
from .models import OperationLog, SystemLog
from django.contrib.auth import get_user_model

User = get_user_model()

class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class SystemLogSerializer(serializers.ModelSerializer):
    """系统日志序列化器"""
    class Meta:
        model = SystemLog
        fields = '__all__'
        read_only_fields = ['created_at']
