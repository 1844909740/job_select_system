from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ChartComponent(models.Model):
    CHART_TYPE = [('line', '折线图'), ('bar', '柱状图'), ('pie', '饼图'), ('scatter', '散点图'), ('radar', '雷达图')]
    name = models.CharField('图表名称', max_length=100)
    chart_type = models.CharField('图表类型', max_length=20, choices=CHART_TYPE)
    data_source = models.JSONField('数据源配置')
    options = models.JSONField('图表选项', default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chart_components')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'chart_components'
