"""
操作日志中间件
"""
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .models import OperationLog

User = get_user_model()

class OperationLogMiddleware(MiddlewareMixin):
    """操作日志中间件"""
    
    def process_request(self, request):
        """请求开始时记录"""
        # 记录请求开始时间
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """响应结束时记录"""
        # 计算执行时间
        execution_time = (time.time() - request.start_time) * 1000
        
        # 排除不需要记录的路径
        exclude_paths = ['/admin/', '/api/token/', '/api/token/refresh/']
        for path in exclude_paths:
            if path in request.path:
                return response
        
        # 只记录成功的请求
        if response.status_code >= 200 and response.status_code < 400:
            # 获取用户
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            if user:
                # 确定操作类型
                action_type = '查询'
                if request.method == 'POST':
                    action_type = '新增'
                elif request.method == 'PUT' or request.method == 'PATCH':
                    action_type = '修改'
                elif request.method == 'DELETE':
                    action_type = '删除'
                
                # 确定模块
                module = '未知'
                path_parts = request.path.strip('/').split('/')
                if len(path_parts) > 1:
                    module = path_parts[1]
                
                # 构建描述
                description = f"{request.method} {request.path}"
                
                # 记录日志
                try:
                    OperationLog.objects.create(
                        user=user,
                        action_type=action_type,
                        module=module,
                        description=description,
                        status='成功',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        request_path=request.path,
                        request_method=request.method,
                        response_code=response.status_code,
                        execution_time=execution_time,
                        extra_data={
                            'query_params': dict(request.GET),
                            'content_type': request.META.get('CONTENT_TYPE'),
                        }
                    )
                except Exception as e:
                    print(f"记录操作日志失败: {str(e)}")
        
        return response
