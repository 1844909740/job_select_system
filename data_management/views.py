"""
数据采集管理视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
import io
from .models import DataSource, DataTask, DataRecord
from .serializers import DataSourceSerializer, DataTaskSerializer, DataRecordSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def one_click_generate(request):
    """一键采集：调用 generate_data 管理命令重新生成 15000 条数据"""
    try:
        out = io.StringIO()
        call_command('generate_data', '--clear', '--count=15000', stdout=out)
        output = out.getvalue()
        return Response({'message': '数据采集完成！已生成 15000 条岗位数据', 'detail': output})
    except Exception as e:
        return Response({'error': f'采集失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        # 更新任务状态为运行中
        task.status = '开发中'
        task.save()
        
        try:
            # 模拟数据采集执行逻辑
            # 实际项目中，这里应该根据数据源类型和配置执行相应的采集操作
            import time
            time.sleep(2)  # 模拟采集过程
            
            # 生成模拟数据
            import random
            mock_data = {
                'title': f'测试岗位{random.randint(1, 1000)}',
                'company': f'测试公司{random.randint(1, 100)}',
                'salary': f'{random.randint(5000, 30000)}-{random.randint(30000, 50000)}',
                'location': '北京',
                'requirements': '熟悉Python，有相关工作经验',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存采集记录
            from .models import DataRecord
            DataRecord.objects.create(
                task=task,
                data=mock_data
            )
            
            # 更新任务状态和运行时间
            task.status = '已完成'
            task.last_run_time = timezone.now()
            # 简单计算下次运行时间（实际项目中应使用cron表达式解析）
            task.next_run_time = timezone.now() + timedelta(days=1)
            task.save()
            
            return Response({'message': f'任务 {task.name} 执行成功', 'collected_data': mock_data})
        except Exception as e:
            # 记录异常信息
            from operation_log.models import SystemLog
            SystemLog.objects.create(
                level='ERROR',
                message=f'数据采集任务执行失败: {str(e)}',
                module='data_management',
                extra_data={
                    'task_id': task.id,
                    'task_name': task.name,
                    'datasource_id': task.data_source.id,
                    'datasource_name': task.data_source.name,
                    'user_id': request.user.id,
                    'user_name': request.user.username
                }
            )
            
            # 更新任务状态为失败
            task.status = '已暂停'
            task.save()
            return Response({'message': f'任务 {task.name} 执行失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
