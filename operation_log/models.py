from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class OperationLog(models.Model):
    ACTION_TYPE = [('查询', '查询'), ('新增', '新增'), ('修改', '修改'), ('删除', '删除'), ('导出', '导出')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operation_logs')
    action_type = models.CharField('操作类型', max_length=20, choices=ACTION_TYPE)
    module = models.CharField('模块', max_length=50)
    description = models.TextField('操作描述')
    ip_address = models.GenericIPAddressField('IP地址', null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'operation_logs'
        ordering = ['-created_at']
