from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import OperationLog, SystemLog
from .serializers import OperationLogSerializer, SystemLogSerializer

class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志视图集"""
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action_type', 'module', 'description', 'status', 'ip_address']
    ordering_fields = ['created_at', 'action_type', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = OperationLog.objects.all()
        
        # 普通用户只能查看自己的日志
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        
        # 过滤参数
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """系统日志视图集"""
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['level', 'message', 'module']
    ordering_fields = ['created_at', 'level']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # 只有超级用户可以查看系统日志
        if not self.request.user.is_superuser:
            return SystemLog.objects.none()
        
        queryset = SystemLog.objects.all()
        
        # 过滤参数
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
