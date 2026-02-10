"""
自定义中间件
"""
import traceback
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from operation_log.models import SystemLog

class ErrorHandlingMiddleware(MiddlewareMixin):
    """错误处理中间件"""
    
    def process_request(self, request):
        """请求开始时记录"""
        # 记录请求开始时间
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """响应结束时记录"""
        # 计算执行时间
        if hasattr(request, 'start_time'):
            execution_time = (time.time() - request.start_time) * 1000
            # 记录慢请求
            if execution_time > 5000:  # 5秒以上的请求
                SystemLog.objects.create(
                    level='WARNING',
                    message=f'慢请求: {request.method} {request.path}',
                    module='middleware',
                    extra_data={
                        'execution_time': execution_time,
                        'method': request.method,
                        'path': request.path,
                        'query_params': dict(request.GET),
                        'user_agent': request.META.get('HTTP_USER_AGENT'),
                        'ip_address': request.META.get('REMOTE_ADDR')
                    }
                )
        return response
    
    def process_exception(self, request, exception):
        """处理异常"""
        # 记录异常信息
        error_trace = traceback.format_exc()
        
        # 记录系统日志
        SystemLog.objects.create(
            level='ERROR',
            message=f'异常: {str(exception)}',
            module='middleware',
            error_trace=error_trace,
            extra_data={
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'ip_address': request.META.get('REMOTE_ADDR'),
                'exception_type': type(exception).__name__
            }
        )
        
        # 返回错误响应
        return JsonResponse(
            {
                'error': '服务器内部错误',
                'message': str(exception),
                'status_code': 500
            },
            status=500
        )
