from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """Called when Django has finished loading all apps"""
        # Import signal handlers or other initialization code here if needed
        pass