# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from telegram import Bot as BotAPI
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

logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class Bot(MicrobotModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bots', help_text=_("User who owns the bot"))
    token = models.CharField(_('Token'), max_length=100, db_index=True, unique=True, validators=[validators.validate_token],
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
    
    @property
    def hook_id(self):
        return str(self.id)
            
    def handle(self, update):
        urlpatterns = []
        state_context = {}
        try:
            chat_state = ChatState.objects.get(chat=update.message.chat, state__bot=self)
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
