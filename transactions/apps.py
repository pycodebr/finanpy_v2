from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    
    def ready(self):
        """
        Import signals when Django starts.
        
        This method is called when the Django application is ready.
        We import signals here to ensure they are registered and will
        respond to model changes throughout the application lifecycle.
        """
        import transactions.signals  # noqa: F401
