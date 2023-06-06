from django.apps import AppConfig


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.mailing'

    def ready(self) -> None:
        import src.mailing.signals
