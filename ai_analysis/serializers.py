from rest_framework import serializers
from .models import AIAnalysisTask

class AIAnalysisTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisTask
        fields = '__all__'
        read_only_fields = ['created_by', 'status', 'result', 'created_at']
