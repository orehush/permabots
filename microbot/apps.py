from django.apps import AppConfig
from django.apps import apps
from django.db.models import signals


def connect_bot_signals():
    from . import signals as handlers
    signals.pre_save.connect(handlers.validate_bot,
                             sender=apps.get_model("microbot", "Bot"),
                             dispatch_uid='bot_validate')
    signals.post_save.connect(handlers.set_bot_webhook,
                              sender=apps.get_model("microbot", "Bot"),
                              dispatch_uid='bot_set_webhook')
    signals.post_save.connect(handlers.set_bot_api_data,
                              sender=apps.get_model("microbot", "Bot"),
                              dispatch_uid='bot_set_api_data')

class MicrobotAppConfig(AppConfig):
    name = "microbot"
    verbose_name = "Microbot"

    def ready(self):
        connect_bot_signals()
