"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/data/', include('data_management.urls')),
    path('api/position/', include('position_data.urls')),
    path('api/statistics/', include('statistics_app.urls')),
    path('api/visualization/', include('visualization.urls')),
    path('api/logs/', include('operation_log.urls')),
    path('api/ai/', include('ai_analysis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
