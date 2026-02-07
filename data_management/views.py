"""
数据采集管理视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DataSource, DataTask, DataRecord
from .serializers import DataSourceSerializer, DataTaskSerializer, DataRecordSerializer


class DataSourceViewSet(viewsets.ModelViewSet):
    """数据源视图集"""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        return DataSource.objects.filter(created_by=self.request.user)


class DataTaskViewSet(viewsets.ModelViewSet):
    """数据采集任务视图集"""
    queryset = DataTask.objects.all()
    serializer_class = DataTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        return DataTask.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """手动运行任务"""
        task = self.get_object()
        # 这里添加实际的任务执行逻辑
        return Response({'message': f'任务 {task.name} 已启动'})
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """暂停任务"""
        task = self.get_object()
        task.status = '已暂停'
        task.save()
        return Response({'message': f'任务 {task.name} 已暂停'})


class DataRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """数据记录视图集（只读）"""
    queryset = DataRecord.objects.all()
    serializer_class = DataRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DataRecord.objects.filter(task__created_by=self.request.user)
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset
