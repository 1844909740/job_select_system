from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class AIAlgorithm(models.Model):
    """AI算法模型"""
    ALGORITHM_TYPE = [
        ('recommendation', '推荐算法'), 
        ('prediction', '预测分析'),
        ('classification', '分类分析'),
        ('clustering', '聚类分析'),
        ('sentiment', '情感分析'),
        ('nlp', '自然语言处理')
    ]
    
    name = models.CharField('算法名称', max_length=100, unique=True)
    algorithm_type = models.CharField('算法类型', max_length=50, choices=ALGORITHM_TYPE)
    description = models.TextField('算法描述')
    parameters = models.JSONField('算法参数', default=dict)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'ai_algorithms'
        verbose_name = 'AI算法'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class AIAnalysisTask(models.Model):
    """AI分析任务模型"""
    TASK_STATUS = [
        ('待开发', '待开发'), 
        ('处理中', '处理中'), 
        ('已完成', '已完成'), 
        ('失败', '失败')
    ]
    
    title = models.CharField('任务标题', max_length=200)
    description = models.TextField('任务描述', blank=True)
    input_data = models.JSONField('输入数据')
    algorithm = models.ForeignKey(AIAlgorithm, on_delete=models.SET_NULL, null=True, related_name='tasks')
    algorithm_type = models.CharField('算法类型', max_length=50, blank=True)
    parameters = models.JSONField('任务参数', default=dict)
    status = models.CharField('状态', max_length=20, choices=TASK_STATUS, default='待开发')
    result = models.JSONField('分析结果', null=True, blank=True)
    error_message = models.TextField('错误信息', null=True, blank=True)
    execution_time = models.FloatField('执行时间(ms)', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tasks')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'ai_analysis_tasks'
        verbose_name = 'AI分析任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class AIAnalysisResult(models.Model):
    """AI分析结果模型"""
    task = models.ForeignKey(AIAnalysisTask, on_delete=models.CASCADE, related_name='result_details')
    result_type = models.CharField('结果类型', max_length=100)
    data = models.JSONField('结果数据')
    metrics = models.JSONField('评估指标', default=dict, blank=True)
    visualization_data = models.JSONField('可视化数据', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'ai_analysis_results'
        verbose_name = 'AI分析结果'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.task.title} - {self.result_type}"
