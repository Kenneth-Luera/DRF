from django.apps import AppConfig


class DrfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tutorial.DRF'

    def ready(self):
        import tutorial.DRF.signals