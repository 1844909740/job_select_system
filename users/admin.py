from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (('额外信息', {'fields': ('phone', 'avatar')}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('额外信息', {'fields': ('phone', 'avatar')}),)
