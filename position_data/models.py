"""
岗位数据查询模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Position(models.Model):
    """岗位信息"""
    POSITION_TYPE = [
        ('全职', '全职'),
        ('兼职', '兼职'),
        ('实习', '实习'),
        ('合同', '合同'),
    ]
    
    title = models.CharField('岗位名称', max_length=200)
    company = models.CharField('公司名称', max_length=200)
    location = models.CharField('工作地点', max_length=100)
    salary_range = models.CharField('薪资范围', max_length=100)
    position_type = models.CharField('岗位类型', max_length=20, choices=POSITION_TYPE)
    requirements = models.TextField('岗位要求')
    description = models.TextField('岗位描述')
    benefits = models.TextField('福利待遇', blank=True)
    education = models.CharField('学历要求', max_length=50)
    experience = models.CharField('经验要求', max_length=50)
    industry = models.CharField('所属行业', max_length=100)
    source_url = models.URLField('来源链接', blank=True)
    published_date = models.DateField('发布日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'positions'
        verbose_name = '岗位信息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['industry']),
            models.Index(fields=['location']),
        ]
        
    def __str__(self):
        return f"{self.title} - {self.company}"


class PositionQuery(models.Model):
    """岗位查询记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='position_queries')
    keywords = models.CharField('关键词', max_length=200)
    filters = models.JSONField('筛选条件', default=dict)
    result_count = models.IntegerField('结果数量', default=0)
    created_at = models.DateTimeField('查询时间', auto_now_add=True)
    
    class Meta:
        db_table = 'position_queries'
        verbose_name = '岗位查询记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.keywords}"


class FavoritePosition(models.Model):
    """收藏的岗位"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_positions')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='favorited_by')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)
    
    class Meta:
        db_table = 'favorite_positions'
        verbose_name = '收藏岗位'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'position']
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.position.title}"
