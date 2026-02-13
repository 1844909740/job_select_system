"""
数据采集管理视图
"""
import subprocess
import os
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
    """一键数据采集 - 调用generate_data.py重新生成15000条数据"""
    
    # 检查权限：只有管理员和超级管理员可以使用
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': '只有管理员和超级管理员可以使用一键数据采集功能'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        # 记录操作开始时间
        start_time = timezone.now()
        
        # 记录操作日志
        from operation_log.models import OperationLog, SystemLog
        OperationLog.objects.create(
            user=request.user,
            action_type='数据采集',
            module='data_management',
            description='开始执行一键数据采集',
            status='进行中',
            ip_address=request.META.get('REMOTE_ADDR'),
            request_path=request.path,
            request_method='POST',
            response_code=200,
        )
        
        # 获取Django项目根目录
        base_dir = settings.BASE_DIR
        
        # 构建管理命令路径
        manage_py_path = os.path.join(base_dir, 'manage.py')
        
        # 执行Django管理命令
        result = subprocess.run([
            'python', manage_py_path, 'generate_data'
        ], 
        cwd=base_dir,
        capture_output=True, 
        text=True, 
        timeout=300  # 5分钟超时
        )
        
        end_time = timezone.now()
        execution_time = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            # 执行成功
            SystemLog.objects.create(
                level='INFO',
                message='一键数据采集执行成功',
                module='data_management',
                extra_data={
                    'user_id': request.user.id,
                    'user_name': request.user.username,
                    'execution_time': execution_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                }
            )
            
            # 更新操作日志状态
            log = OperationLog.objects.filter(
                user=request.user,
                action_type='数据采集',
                status='进行中'
            ).order_by('-created_at').first()
            if log:
                log.status = '成功'
                log.description = f'一键数据采集完成，耗时 {execution_time:.2f} 秒'
                log.save()
            
            return Response({
                'message': '数据采集完成！已成功生成15000条岗位数据',
                'execution_time': f'{execution_time:.2f}秒',
                'details': result.stdout
            })
        else:
            # 执行失败
            error_msg = result.stderr or result.stdout or '未知错误'
            
            SystemLog.objects.create(
                level='ERROR',
                message=f'一键数据采集执行失败: {error_msg}',
                module='data_management',
                extra_data={
                    'user_id': request.user.id,
                    'user_name': request.user.username,
                    'execution_time': execution_time,
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                }
            )
            
            # 更新操作日志状态
            log = OperationLog.objects.filter(
                user=request.user,
                action_type='数据采集',
                status='进行中'
            ).order_by('-created_at').first()
            if log:
                log.status = '失败'
                log.description = f'一键数据采集失败: {error_msg}'
                log.save()
            
            return Response({
                'error': f'数据采集失败: {error_msg}',
                'details': result.stderr
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except subprocess.TimeoutExpired:
        SystemLog.objects.create(
            level='ERROR',
            message='一键数据采集执行超时',
            module='data_management',
            extra_data={
                'user_id': request.user.id,
                'user_name': request.user.username,
                'timeout': 300,
            }
        )
        
        return Response({
            'error': '数据采集执行超时（超过5分钟），请稍后重试'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except Exception as e:
        SystemLog.objects.create(
            level='ERROR',
            message=f'一键数据采集异常: {str(e)}',
            module='data_management',
            extra_data={
                'user_id': request.user.id,
                'user_name': request.user.username,
                'error': str(e),
            }
        )
        
        return Response({
            'error': f'数据采集异常: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
