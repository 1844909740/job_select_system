"""
数据采集管理视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def one_click_data_collection(request):
    """一键数据采集 - 从招聘网站爬取岗位数据"""

    # 检查权限：只有管理员和超级管理员可以使用
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': '只有管理员和超级管理员可以使用一键数据采集功能'},
                       status=status.HTTP_403_FORBIDDEN)

    from operation_log.models import OperationLog, SystemLog

    try:
        from position_data.job_scraper import run_full_scrape

        result = run_full_scrape(max_total=500)

        # 记录系统日志
        SystemLog.objects.create(
            level='INFO',
            message=f'数据爬取完成: {result["message"]}',
            module='data_management',
            extra_data={
                'user_id': request.user.id,
                'user_name': request.user.username,
                'total_collected': result.get('total_collected', 0),
                'total_imported': result.get('total_imported', 0),
                'elapsed_seconds': result.get('elapsed_seconds', 0),
            }
        )

        # 记录操作日志
        OperationLog.objects.create(
            user=request.user,
            action_type='数据采集',
            module='data_management',
            description=result['message'],
            status='成功' if result['success'] else '失败',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )

        return Response({
            'success': result['success'],
            'message': result['message'],
            'total_collected': result.get('total_collected', 0),
            'total_imported': result.get('total_imported', 0),
            'elapsed_seconds': result.get('elapsed_seconds', 0),
        })

    except Exception as e:
        SystemLog.objects.create(
            level='ERROR',
            message=f'数据爬取异常: {str(e)}',
            module='data_management',
            extra_data={
                'user_id': request.user.id,
                'user_name': request.user.username,
                'error': str(e),
            }
        )
        OperationLog.objects.create(
            user=request.user,
            action_type='数据采集',
            module='data_management',
            description=f'爬取异常: {str(e)}',
            status='失败',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )
        return Response({'error': f'数据采集失败: {str(e)}'},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
