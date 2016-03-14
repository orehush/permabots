# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from telegram import Bot as BotAPI
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
import logging
from microbot.models import User
from django.core.urlresolvers import RegexURLResolver
from django.core.urlresolvers import Resolver404
from telegram import ParseMode, ReplyKeyboardHide, ReplyKeyboardMarkup
import ast
from django.conf import settings

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Bot(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bots')
    token = models.CharField(_('Token'), max_length=100, db_index=True)
    user_api = models.OneToOneField(User, verbose_name=_("Bot User"), related_name='bot', 
                                    on_delete=models.CASCADE, blank=True, null=True)
    enabled = models.BooleanField(_('Enable'), default=True)
    created = models.DateTimeField(('Date Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Date Modified'), auto_now=True)    
    
    class Meta:
        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')    
    
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self._bot = None
        if self.token:
            self._bot = BotAPI(self.token)
            
    def __str__(self):
        return "%s" % (self.user_api.first_name or self.token if self.user_api else self.token)
            
    def handle(self, update):
        urlpatterns = []
        for handler in self.handlers.filter(enabled=True):
            urlpatterns.append(handler.urlpattern())
        resolver = RegexURLResolver(r'^', urlpatterns)
        try:
            resolver_match = resolver.resolve(update.message.text)
        except Resolver404:
            logger.warning("Handler not found for %s" % update)
        else:
            callback, callback_args, callback_kwargs = resolver_match
            logger.debug("Calling callback:%s for update %s with %s" % 
                         (callback, update, callback_kwargs))
            text, keyboard = callback(self, update=update, **callback_kwargs)
            if keyboard:
                keyboard = ast.literal_eval(keyboard)
                keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            else:
                keyboard = ReplyKeyboardHide()
            self.send_message(chat_id=update.message.chat.id, 
                              text=text.encode('utf-8'), reply_markup=keyboard, parse_mode=ParseMode.HTML)
        
    def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        self._bot.sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode, 
                              disable_web_page_preview=disable_web_page_preview, **kwargs)        
        logger.debug("Message sent:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,kwargs:%s" %
                     (chat_id, text, parse_mode, disable_web_page_preview, kwargs))

@receiver(post_save, sender=Bot)
def set_api(sender, instance, **kwargs):
    #  set bot api if not yet
    if not instance._bot:
        instance._bot = BotAPI(instance.token)

    # set webhook
    url = None
    if instance.enabled:
        webhook = reverse('microbot:telegrambot', kwargs={'token': instance.token})        
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        url = 'https://' + current_site.domain + webhook   
    instance._bot.setWebhook(webhook_url=url)
    logger.info("Success: Webhook url %s for bot %s set" % (url, str(instance)))
    
    #  complete  Bot instance with api data
    if not instance.user_api:
        bot_api = instance._bot.getMe()
        user_api, _ = User.objects.get_or_create(**bot_api.to_dict())
        instance.user_api = user_api
        instance.save()
        logger.info("Success: Bot api info for bot %s set" % str(instance))