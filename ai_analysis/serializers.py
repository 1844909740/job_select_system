from rest_framework import serializers
from .models import AIAnalysisTask, AIAlgorithm, AIAnalysisResult

class AIAlgorithmSerializer(serializers.ModelSerializer):
    """AI算法序列化器"""
    class Meta:
        model = AIAlgorithm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    """AI分析结果序列化器"""
    class Meta:
        model = AIAnalysisResult
        fields = '__all__'
        read_only_fields = ['created_at']


class AIAnalysisTaskSerializer(serializers.ModelSerializer):
    """AI分析任务序列化器"""
    algorithm = AIAlgorithmSerializer(read_only=True)
    algorithm_id = serializers.PrimaryKeyRelatedField(
        queryset=AIAlgorithm.objects.all(),
        write_only=True,
        source='algorithm',
        required=False
    )
    result_details = AIAnalysisResultSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AIAnalysisTask
        fields = [
            'id', 'title', 'description', 'input_data', 'algorithm', 'algorithm_id', 
            'algorithm_type', 'parameters', 'status', 'result', 'error_message', 
            'execution_time', 'result_details', 'created_by', 'created_by_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'status', 'result', 'error_message', 'execution_time', 'created_at', 'updated_at']
