from django.contrib import admin
from .models import Position, PositionQuery, FavoritePosition

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'industry', 'created_at']

@admin.register(PositionQuery)
class PositionQueryAdmin(admin.ModelAdmin):
    list_display = ['user', 'keywords', 'result_count', 'created_at']

@admin.register(FavoritePosition)
class FavoritePositionAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'created_at']
