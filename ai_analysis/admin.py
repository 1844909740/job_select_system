from django.contrib import admin
from .models import AIAnalysisTask
@admin.register(AIAnalysisTask)
class AIAnalysisTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'algorithm', 'status', 'created_by', 'created_at']
