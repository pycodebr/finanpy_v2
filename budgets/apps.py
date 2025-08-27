from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgets'
    verbose_name = 'Budget Management'
    
    def ready(self):
        """
        Import signals when Django starts.
        
        This method is called when the app registry is fully populated.
        We import our signals here to ensure they are connected when
        the application starts up.
        """
        try:
            import budgets.signals  # noqa
        except ImportError:
            pass
