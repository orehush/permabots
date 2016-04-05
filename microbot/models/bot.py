# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from telegram import Bot as BotAPI
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
import logging
from microbot.models.base import MicrobotModel
from microbot.models import User, ChatState
from django.core.urlresolvers import RegexURLResolver
from django.core.urlresolvers import Resolver404
from telegram import ParseMode, ReplyKeyboardHide, ReplyKeyboardMarkup
from telegram.bot import InvalidToken
import ast
from django.conf import settings
from django.db.models import Q
from microbot import validators
import re
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def validate_token(value):
    if not re.match('[0-9]+:[-_a-zA-Z0-9]+', value):
        raise ValidationError(_("%(value)s is not a valid token"), params={'value': value})

@python_2_unicode_compatible
class Bot(MicrobotModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bots', help_text=_("User who owns the bot"))
    token = models.CharField(_('Token'), max_length=100, db_index=True, validators=[validators.validate_token],
                             help_text=_("Token provided by Telegram API https://core.telegram.org/bots"))
    user_api = models.OneToOneField(User, verbose_name=_("Bot User"), related_name='bot', 
                                    on_delete=models.CASCADE, blank=True, null=True,
                                    help_text=_("Telegram API info. Automatically retrieved from Telegram"))
    enabled = models.BooleanField(_('Enable'), default=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')    
    
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self._bot = None
        if self.token:
            try:
                self._bot = BotAPI(self.token)
            except InvalidToken:
                logger.warning("Incorrect token %s" % self.token)
            
    def __str__(self):
        return "%s" % (self.user_api.first_name or self.token if self.user_api else self.token)
            
    def handle(self, update):
        urlpatterns = []
        state_context = {}
        try:
            chat_state = ChatState.objects.get(chat=update.message.chat)
            state_context = chat_state.ctx
            for handler in self.handlers.filter(Q(enabled=True), Q(source_states=chat_state.state) | Q(source_states=None)):
                urlpatterns.append(handler.urlpattern())
        except ChatState.DoesNotExist:
            for handler in self.handlers.filter(enabled=True, source_states=None):
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
            text, keyboard = callback(self, update=update, state_context=state_context, **callback_kwargs)
            if keyboard:
                keyboard = ast.literal_eval(keyboard)
                keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            else:
                keyboard = ReplyKeyboardHide()
            self.send_message(chat_id=update.message.chat.id, 
                              text=text.encode('utf-8'), reply_markup=keyboard, parse_mode=ParseMode.HTML)

    def handle_hook(self, hook, data):
        logger.debug("Calling hook %s process: with %s" % (hook.key, data))
        text, keyboard = hook.process(self, data)
        if keyboard:
                keyboard = ast.literal_eval(keyboard)
                keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        else:
                keyboard = ReplyKeyboardHide()
        for recipient in hook.recipients.all():
            self.send_message(chat_id=recipient.chat_id, 
                              text=text.encode('utf-8'), reply_markup=keyboard, parse_mode=ParseMode.HTML)
            
    def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        try:
            logger.debug("Message to send:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,kwargs:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, kwargs))
            self._bot.sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode, 
                                  disable_web_page_preview=disable_web_page_preview, **kwargs)        
            logger.debug("Message sent OK:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,kwargs:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, kwargs))
        except:
            logger.error("Error trying to send message:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,kwargs:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, kwargs))
        
@receiver(pre_save, sender=Bot)
def validate_bot(sender, instance, **kwargs):
    validate_token(instance.token)
    
@receiver(post_save, sender=Bot)
def set_api(sender, instance, **kwargs):
    #  set bot api if not yet
    if not instance._bot:
        instance._bot = BotAPI(instance.token)
    try:
        # set webhook
        url = None
        if instance.enabled:
            webhook = reverse('microbot:telegrambot', kwargs={'token': instance.token})        
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            url = 'https://' + current_site.domain + webhook   
        instance._bot.setWebhook(webhook_url=url)
        logger.info("Success: Webhook url %s for bot %s set" % (url, str(instance)))
        
    except:
        instance.delete()
        logger.error("Failure: Webhook url %s for bot %s not set" % (url, str(instance)))
        raise
    
    try:
        #  complete  Bot instance with api data
        if not instance.user_api:
            bot_api = instance._bot.getMe()
            user_api, _ = User.objects.get_or_create(**bot_api.to_dict())
            instance.user_api = user_api
            instance.save()
            logger.info("Success: Bot api info for bot %s set" % str(instance))
    except:
        instance.delete()
        logger.error("Failure: Bot api info for bot %s no set" % str(instance))
        raise        