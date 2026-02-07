"""
数据采集管理模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DataSource(models.Model):
    """数据源"""
    TASK_STATUS = [
        ('待开发', '待开发'),
        ('开发中', '开发中'),
        ('已完成', '已完成'),
        ('已暂停', '已暂停'),
    ]
    
    name = models.CharField('数据源名称', max_length=100)
    description = models.TextField('描述', blank=True)
    source_type = models.CharField('数据源类型', max_length=50)
    config = models.JSONField('配置信息', default=dict)
    status = models.CharField('状态', max_length=20, choices=TASK_STATUS, default='待开发')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'data_sources'
        verbose_name = '数据源'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class DataTask(models.Model):
    """数据采集任务"""
    TASK_STATUS = [
        ('待开发', '待开发'),
        ('开发中', '开发中'),
        ('已完成', '已完成'),
        ('已暂停', '已暂停'),
    ]
    
    name = models.CharField('任务名称', max_length=100)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='tasks')
    schedule = models.CharField('调度规则', max_length=100, help_text='Cron表达式')
    status = models.CharField('状态', max_length=20, choices=TASK_STATUS, default='待开发')
    last_run_time = models.DateTimeField('最后运行时间', null=True, blank=True)
    next_run_time = models.DateTimeField('下次运行时间', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_tasks')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'data_tasks'
        verbose_name = '数据采集任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class DataRecord(models.Model):
    """数据记录"""
    task = models.ForeignKey(DataTask, on_delete=models.CASCADE, related_name='records')
    data = models.JSONField('数据内容')
    collected_at = models.DateTimeField('采集时间', auto_now_add=True)
    
    class Meta:
        db_table = 'data_records'
        verbose_name = '数据记录'
        verbose_name_plural = verbose_name
        ordering = ['-collected_at']
        
    def __str__(self):
        return f"{self.task.name} - {self.collected_at}"
