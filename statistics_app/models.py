"""
统计分析模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StatisticsReport(models.Model):
    """统计报告"""
    REPORT_TYPE = [
        ('行业分析', '行业分析'),
        ('薪资分析', '薪资分析'),
        ('地域分析', '地域分析'),
        ('趋势分析', '趋势分析'),
        ('综合分析', '综合分析'),
    ]
    
    title = models.CharField('报告标题', max_length=200)
    report_type = models.CharField('报告类型', max_length=50, choices=REPORT_TYPE)
    parameters = models.JSONField('分析参数', default=dict)
    result_data = models.JSONField('结果数据', default=dict)
    charts = models.JSONField('图表数据', default=list)
    summary = models.TextField('摘要', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statistics_reports')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'statistics_reports'
        verbose_name = '统计报告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class IndustryStatistics(models.Model):
    """行业统计数据"""
    industry = models.CharField('行业名称', max_length=100, unique=True)
    total_positions = models.IntegerField('岗位总数', default=0)
    avg_salary = models.DecimalField('平均薪资', max_digits=10, decimal_places=2, null=True)
    top_companies = models.JSONField('热门公司', default=list)
    hot_skills = models.JSONField('热门技能', default=list)
    growth_rate = models.DecimalField('增长率', max_digits=5, decimal_places=2, null=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'industry_statistics'
        verbose_name = '行业统计'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.industry


class SalaryStatistics(models.Model):
    """薪资统计数据"""
    position_title = models.CharField('岗位名称', max_length=200)
    location = models.CharField('地点', max_length=100)
    min_salary = models.DecimalField('最低薪资', max_digits=10, decimal_places=2)
    max_salary = models.DecimalField('最高薪资', max_digits=10, decimal_places=2)
    avg_salary = models.DecimalField('平均薪资', max_digits=10, decimal_places=2)
    median_salary = models.DecimalField('中位数薪资', max_digits=10, decimal_places=2, null=True)
    sample_size = models.IntegerField('样本数量', default=0)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'salary_statistics'
        verbose_name = '薪资统计'
        verbose_name_plural = verbose_name
        unique_together = ['position_title', 'location']
        
    def __str__(self):
        return f"{self.position_title} - {self.location}"
