from django.apps import AppConfig


class EComerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_comerce'
    
    def ready(self) -> None:
        import e_comerce.signals
        return super().ready()
