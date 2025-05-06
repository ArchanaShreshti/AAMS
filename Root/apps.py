from django.apps import AppConfig

class RootConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Root'

    def ready(self):
        import Root.signals  # Import signals to ensure they are connected when app is ready