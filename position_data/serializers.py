"""
岗位数据查询序列化器
"""
from rest_framework import serializers
from .models import Position, PositionQuery, FavoritePosition


class PositionSerializer(serializers.ModelSerializer):
    """岗位信息序列化器"""
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = '__all__'
        
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoritePosition.objects.filter(
                user=request.user, 
                position=obj
            ).exists()
        return False


class PositionQuerySerializer(serializers.ModelSerializer):
    """岗位查询记录序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PositionQuery
        fields = '__all__'
        read_only_fields = ['user', 'result_count', 'created_at']


class FavoritePositionSerializer(serializers.ModelSerializer):
    """收藏岗位序列化器"""
    position_detail = PositionSerializer(source='position', read_only=True)
    
    class Meta:
        model = FavoritePosition
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
