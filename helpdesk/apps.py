from django.apps import AppConfig


class HelpdeskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'helpdesk'

    def ready(self):
        from .mail.schedule import start_schedule
        start_schedule()