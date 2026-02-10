from rest_framework import serializers
from .models import ChartComponent, Dashboard

class ChartComponentSerializer(serializers.ModelSerializer):
    """图表组件序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ChartComponent
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """仪表盘序列化器"""
    charts = ChartComponentSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
