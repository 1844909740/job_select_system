from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Dashboard(models.Model):
    """仪表盘模型"""
    name = models.CharField('仪表盘名称', max_length=100, unique=True)
    description = models.TextField('仪表盘描述', blank=True)
    layout = models.JSONField('布局配置', default=list)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'dashboards'
        verbose_name = '仪表盘'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class ChartComponent(models.Model):
    """图表组件模型"""
    CHART_TYPE = [
        ('line', '折线图'), 
        ('bar', '柱状图'), 
        ('pie', '饼图'), 
        ('scatter', '散点图'), 
        ('radar', '雷达图'),
        ('area', '面积图'),
        ('gauge', '仪表盘'),
        ('heatmap', '热力图'),
        ('treemap', '树图')
    ]
    
    DATA_SOURCE_TYPE = [
        ('api', 'API接口'),
        ('model', '数据库模型'),
        ('static', '静态数据')
    ]
    
    name = models.CharField('图表名称', max_length=100)
    chart_type = models.CharField('图表类型', max_length=20, choices=CHART_TYPE)
    data_source_type = models.CharField('数据源类型', max_length=20, choices=DATA_SOURCE_TYPE, default='api')
    data_source = models.JSONField('数据源配置')
    options = models.JSONField('图表选项', default=dict)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.SET_NULL, null=True, blank=True, related_name='charts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chart_components')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'chart_components'
        verbose_name = '图表组件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
