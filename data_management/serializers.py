"""
数据采集管理序列化器
"""
from rest_framework import serializers
from .models import DataSource, DataTask, DataRecord


class DataSourceSerializer(serializers.ModelSerializer):
    """数据源序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataSource
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class DataTaskSerializer(serializers.ModelSerializer):
    """数据采集任务序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    
    class Meta:
        model = DataTask
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class DataRecordSerializer(serializers.ModelSerializer):
    """数据记录序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    
    class Meta:
        model = DataRecord
        fields = '__all__'
        read_only_fields = ['collected_at']
