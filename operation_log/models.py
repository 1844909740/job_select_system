from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class OperationLog(models.Model):
    """操作日志模型"""
    ACTION_TYPE = [
        ('查询', '查询'), 
        ('新增', '新增'), 
        ('修改', '修改'), 
        ('删除', '删除'), 
        ('导出', '导出'),
        ('登录', '登录'),
        ('登出', '登出'),
        ('导入', '导入'),
        ('授权', '授权'),
        ('取消授权', '取消授权')
    ]
    
    STATUS = [
        ('成功', '成功'),
        ('失败', '失败'),
        ('警告', '警告')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operation_logs')
    action_type = models.CharField('操作类型', max_length=20, choices=ACTION_TYPE)
    module = models.CharField('模块', max_length=50)
    description = models.TextField('操作描述')
    status = models.CharField('操作状态', max_length=20, choices=STATUS, default='成功')
    ip_address = models.GenericIPAddressField('IP地址', null=True)
    user_agent = models.CharField('用户代理', max_length=500, null=True, blank=True)
    request_path = models.CharField('请求路径', max_length=500, null=True, blank=True)
    request_method = models.CharField('请求方法', max_length=20, null=True, blank=True)
    response_code = models.IntegerField('响应代码', null=True, blank=True)
    execution_time = models.FloatField('执行时间(ms)', null=True, blank=True)
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['module', 'status']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.module}"


class SystemLog(models.Model):
    """系统日志模型"""
    LOG_LEVEL = [
        ('DEBUG', '调试'),
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('CRITICAL', '严重')
    ]
    
    level = models.CharField('日志级别', max_length=20, choices=LOG_LEVEL)
    message = models.TextField('日志消息')
    module = models.CharField('模块', max_length=100, null=True, blank=True)
    error_trace = models.TextField('错误堆栈', null=True, blank=True)
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['module']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.level} - {self.message[:50]}"
