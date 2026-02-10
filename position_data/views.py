"""
岗位数据查询视图
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.cache import cache
import hashlib
import json
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
        # 生成缓存键
        cache_key = self._generate_cache_key()
        
        # 尝试从缓存获取
        cached_queryset = cache.get(cache_key)
        if cached_queryset is not None:
            return cached_queryset
        
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
        
        # 经验筛选
        experience = self.request.query_params.get('experience')
        if experience and experience != '不限':
            queryset = queryset.filter(experience__icontains=experience)

        # 学历筛选
        education = self.request.query_params.get('education')
        if education and education != '不限':
            queryset = queryset.filter(education__icontains=education)

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
        
        # 缓存查询结果，有效期5分钟
        cache.set(cache_key, queryset, 300)
        
        return queryset
    
    def _generate_cache_key(self):
        """生成缓存键"""
        # 收集所有查询参数
        params = dict(self.request.query_params)
        # 排序参数以确保一致性
        sorted_params = sorted(params.items())
        # 转换为字符串
        params_str = json.dumps(sorted_params, sort_keys=True)
        # 生成MD5哈希
        hash_obj = hashlib.md5(params_str.encode())
        # 生成缓存键
        cache_key = f"position_query:{hash_obj.hexdigest()}"
        return cache_key
    
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
            # 清除缓存
            self._clear_cache()
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
            # 清除缓存
            self._clear_cache()
            return Response({'message': '已取消收藏'})
        return Response({'message': '未找到收藏记录'}, status=status.HTTP_400_BAD_REQUEST)
    
    def _clear_cache(self):
        """清除缓存"""
        # 清除当前查询的缓存
        cache_key = self._generate_cache_key()
        cache.delete(cache_key)


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
