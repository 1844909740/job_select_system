from django.contrib import admin
from .models import ChartComponent
@admin.register(ChartComponent)
class ChartComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'chart_type', 'created_by', 'created_at']
