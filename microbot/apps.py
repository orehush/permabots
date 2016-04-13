from django.apps import AppConfig
from django.apps import apps
from django.db.models import signals


def connect_bot_signals():
    from . import signals as handlers
    sender = apps.get_model("microbot", "Bot")
    signals.pre_save.connect(handlers.validate_bot,
                             sender=sender,
                             dispatch_uid='bot_validate')
    signals.post_save.connect(handlers.set_bot_webhook,
                              sender=sender,
                              dispatch_uid='bot_set_webhook')
    signals.post_save.connect(handlers.set_bot_api_data,
                              sender=sender,
                              dispatch_uid='bot_set_api_data')
    signals.post_save.connect(handlers.delete_cache,
                              sender=sender,
                              dispatch_uid='bot_delete_cache')
    
def connect_telegram_api_signals():
    from . import signals as handlers
    chat = apps.get_model("microbot", "Chat")
    user = apps.get_model("microbot", "User")
    signals.post_save.connect(handlers.delete_cache,
                              sender=chat,
                              dispatch_uid='bot_delete_cache')
    signals.post_save.connect(handlers.delete_cache,
                              sender=user,
                              dispatch_uid='bot_delete_cache')

class MicrobotAppConfig(AppConfig):
    name = "microbot"
    verbose_name = "Microbot"

    def ready(self):
        connect_bot_signals()
        connect_telegram_api_signals()