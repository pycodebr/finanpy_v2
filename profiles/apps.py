from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'
    
    def ready(self):
        """
        Import signals when the app is ready.
        
        This ensures that the signal handlers are connected and will
        automatically create Profile objects when Users are created.
        """
        import profiles.signals
