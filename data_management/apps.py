from django.apps import AppConfig

class DataManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_management'
    verbose_name = '数据采集管理'
