from django.contrib import admin
from .models import DataSource, DataTask, DataRecord

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'status', 'created_by', 'created_at']

@admin.register(DataTask)
class DataTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_source', 'status', 'schedule', 'created_at']

@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'collected_at']
