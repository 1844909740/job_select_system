"""
统计分析序列化器
"""
from rest_framework import serializers
from .models import StatisticsReport, IndustryStatistics, SalaryStatistics


class StatisticsReportSerializer(serializers.ModelSerializer):
    """统计报告序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StatisticsReport
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class IndustryStatisticsSerializer(serializers.ModelSerializer):
    """行业统计序列化器"""
    class Meta:
        model = IndustryStatistics
        fields = '__all__'
        read_only_fields = ['updated_at']


class SalaryStatisticsSerializer(serializers.ModelSerializer):
    """薪资统计序列化器"""
    class Meta:
        model = SalaryStatistics
        fields = '__all__'
        read_only_fields = ['updated_at']
