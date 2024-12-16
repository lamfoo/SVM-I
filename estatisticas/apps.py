from django.apps import AppConfig

class EstatisticasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estatisticas'

    def ready(self):
        import estatisticas.signals  # Nome correto do app
