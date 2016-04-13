from telegram import Bot as BotAPI
from django.core.urlresolvers import reverse
from django.conf import settings
import logging
from microbot.validators import validate_token
from django.apps import apps
from microbot import caching

logger = logging.getLogger(__name__)

def set_bot_webhook(sender, instance, **kwargs):
    def get_site_domain():
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        return current_site.domain
    
    #  set bot api if not yet
    if not instance._bot:
        instance._bot = BotAPI(instance.token)
    try:
        # set webhook
        url = None
        if instance.enabled:
            webhook = reverse('microbot:telegrambot', kwargs={'hook_id': instance.hook_id})
            url = 'https://' + getattr(settings, 'MICROBOT_WEBHOOK_DOMAIN', get_site_domain()) + webhook   
        instance._bot.setWebhook(webhook_url=url)
        logger.info("Success: Webhook url %s for bot %s set" % (url, str(instance)))
        
    except:
        instance.delete()
        logger.error("Failure: Webhook url %s for bot %s not set" % (url, str(instance)))
        raise
    
def set_bot_api_data(sender, instance, **kwargs):
        #  set bot api if not yet
    if not instance._bot:
        instance._bot = BotAPI(instance.token)
    
    try:
        #  complete  Bot instance with api data
        if not instance.user_api:
            bot_api = instance._bot.getMe()
            User = apps.get_model('microbot', 'User')
            user_api, _ = User.objects.get_or_create(**bot_api.to_dict())
            instance.user_api = user_api
            instance.save()
            logger.info("Success: Bot api info for bot %s set" % str(instance))
    except:
        instance.delete()
        logger.error("Failure: Bot api info for bot %s no set" % str(instance))
        raise  
    
def validate_bot(sender, instance, **kwargs):
    validate_token(instance.token)
    
def delete_cache(sender, instance, **kwargs):
    caching.delete(sender, instance.id)
