from django.contrib import admin
from .models import StatisticsReport, IndustryStatistics, SalaryStatistics

@admin.register(StatisticsReport)
class StatisticsReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'created_by', 'created_at']

@admin.register(IndustryStatistics)
class IndustryStatisticsAdmin(admin.ModelAdmin):
    list_display = ['industry', 'total_positions', 'avg_salary', 'updated_at']

@admin.register(SalaryStatistics)
class SalaryStatisticsAdmin(admin.ModelAdmin):
    list_display = ['position_title', 'location', 'avg_salary', 'sample_size']
