"""
岗位数据查询视图
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Position, PositionQuery, FavoritePosition
from .serializers import (
    PositionSerializer, 
    PositionQuerySerializer, 
    FavoritePositionSerializer
)


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    """岗位信息视图集"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company', 'location', 'industry']
    ordering_fields = ['created_at', 'published_date', 'salary_range']
    
    def get_queryset(self):
        queryset = Position.objects.all()
        
        # 关键词搜索
        keywords = self.request.query_params.get('keywords')
        if keywords:
            queryset = queryset.filter(
                Q(title__icontains=keywords) |
                Q(company__icontains=keywords) |
                Q(description__icontains=keywords)
            )
        
        # 地点筛选
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # 行业筛选
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        # 岗位类型筛选
        position_type = self.request.query_params.get('position_type')
        if position_type:
            queryset = queryset.filter(position_type=position_type)
        
        # 保存查询记录
        if keywords:
            PositionQuery.objects.create(
                user=self.request.user,
                keywords=keywords,
                filters=dict(self.request.query_params),
                result_count=queryset.count()
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """收藏岗位"""
        position = self.get_object()
        favorite, created = FavoritePosition.objects.get_or_create(
            user=request.user,
            position=position,
            defaults={'notes': request.data.get('notes', '')}
        )
        if created:
            return Response({'message': '收藏成功'})
        return Response({'message': '已经收藏过了'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unfavorite(self, request, pk=None):
        """取消收藏"""
        position = self.get_object()
        deleted, _ = FavoritePosition.objects.filter(
            user=request.user,
            position=position
        ).delete()
        if deleted:
            return Response({'message': '已取消收藏'})
        return Response({'message': '未找到收藏记录'}, status=status.HTTP_400_BAD_REQUEST)


class PositionQueryViewSet(viewsets.ReadOnlyModelViewSet):
    """岗位查询记录视图集"""
    serializer_class = PositionQuerySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PositionQuery.objects.filter(user=self.request.user)


class FavoritePositionViewSet(viewsets.ModelViewSet):
    """收藏岗位视图集"""
    serializer_class = FavoritePositionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavoritePosition.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
