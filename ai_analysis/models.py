from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class AIAnalysisTask(models.Model):
    TASK_STATUS = [('待开发', '待开发'), ('处理中', '处理中'), ('已完成', '已完成'), ('失败', '失败')]
    ALGORITHM_TYPE = [('recommendation', '推荐算法'), ('prediction', '预测分析')]
    title = models.CharField('任务标题', max_length=200)
    input_data = models.JSONField('输入数据')
    algorithm = models.CharField('算法类型', max_length=50, choices=ALGORITHM_TYPE)
    status = models.CharField('状态', max_length=20, choices=TASK_STATUS, default='待开发')
    result = models.JSONField('分析结果', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tasks')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'ai_analysis_tasks'
