from rest_framework import serializers
from .models import ChartComponent

class ChartComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartComponent
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']
