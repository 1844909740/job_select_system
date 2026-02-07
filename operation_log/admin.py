from django.contrib import admin
from .models import OperationLog
@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'module', 'ip_address', 'created_at']
