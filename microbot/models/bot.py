# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from telegram import Bot as BotAPI
import logging
from microbot.models.base import MicrobotModel
from microbot.models import User, TelegramChatState
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
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Name for the handler"))
    telegram_bot = models.OneToOneField('TelegramBot', verbose_name=_("Telegram Bot"), related_name='bot', 
                                        on_delete=models.SET_NULL, blank=True, null=True,
                                        help_text=_("Telegram Bot"))

    class Meta:
        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')    
        
    def __str__(self):
        return '%s' % self.name
    
    def handle_message(self, message, bot_service):
        urlpatterns = []
        state_context = {}
        chat_state = bot_service.get_chat_state(message)
        if chat_state:
            state_context = chat_state.ctx
            for handler in self.handlers.filter(Q(enabled=True), Q(source_states=chat_state.state) | Q(source_states=None)):
                urlpatterns.append(handler.urlpattern())
        else:
            for handler in self.handlers.filter(enabled=True, source_states=None):
                urlpatterns.append(handler.urlpattern())
        
        resolver = RegexURLResolver(r'^', urlpatterns)
        try:
            resolver_match = resolver.resolve(bot_service.message_text(message))
        except Resolver404:
            logger.warning("Handler not found for %s" % message)
        else:
            callback, callback_args, callback_kwargs = resolver_match
            logger.debug("Calling callback:%s for message %s with %s" % 
                         (callback, message, callback_kwargs))
            text, keyboard, target_state, context = callback(self, message=message, state_context=state_context, **callback_kwargs)
            if target_state:
                bot_service.update_chat_state(message, chat_state, target_state, context)
            keyboard = bot_service.build_keyboard(keyboard)
            bot_service.send_message(bot_service.get_sender(message), text, keyboard)
            
    def handle_hook(self, hook, data):
        logger.debug("Calling hook %s process: with %s" % (hook.key, data))
        text, keyboard = hook.process(self, data)
        if hook.bot.telegram_bot.enabled:
            keyboard = hook.bot.telegram_bot.build_keyboard(keyboard)
            for recipient in hook.telegram_recipients.all():
                hook.bot.telegram_bot.send_message(recipient.chat_id, text, keyboard)


@python_2_unicode_compatible
class TelegramBot(MicrobotModel):    
    token = models.CharField(_('Token'), max_length=100, db_index=True, unique=True, validators=[validators.validate_token],
                             help_text=_("Token provided by Telegram API https://core.telegram.org/bots"))
    user_api = models.OneToOneField(User, verbose_name=_("Telegram Bot User"), related_name='telegram_bot', 
                                    on_delete=models.CASCADE, blank=True, null=True,
                                    help_text=_("Telegram API info. Automatically retrieved from Telegram"))
    enabled = models.BooleanField(_('Enable'), default=True, help_text=_("Enable/disable telegram bot"))
    
    class Meta:
        verbose_name = _('Telegram Bot')
        verbose_name_plural = _('Telegram Bots')    
    
    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__(*args, **kwargs)
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
    
    def message_text(self, message):
        return message.text
    
    def get_chat_state(self, message):
        try:
            return TelegramChatState.objects.get(chat=message.chat, state__bot=self.bot)
        except TelegramChatState.DoesNotExist:
            return None
        
    def build_keyboard(self, keyboard):       
        if keyboard:
            keyboard = ast.literal_eval(keyboard)
            keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        else:
            keyboard = ReplyKeyboardHide()
        return keyboard
            
    def update_chat_state(self, message, chat_state, target_state, context):
        if not chat_state:
                logger.warning("Chat state for update chat %s not exists" % 
                               (message.chat.id))
                TelegramChatState.objects.create(chat=message.chat,
                                                 state=target_state,
                                                 ctx=context)
        else:
            if chat_state.state != target_state:
                chat_state.state = target_state
                chat_state.ctx = context
                chat_state.save()
                logger.debug("Chat state updated:%s for message %s with %s" % 
                             (target_state, message, context))
            else:
                logger.debug("ChateState stays in %s" % target_state)
        
    def get_sender(self, message):
        return message.chat.id
        
    def send_message(self, chat_id, text, keyboard):
        parse_mode = ParseMode.HTML
        text = text.encode('utf-8')
        disable_web_page_preview = None
        try:
            logger.debug("Message to send:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,keyboard:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, keyboard))
            self._bot.sendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode, 
                                  disable_web_page_preview=disable_web_page_preview, reply_markup=keyboard)        
            logger.debug("Message sent OK:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,reply_keyboard:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, keyboard))
        except:
            logger.error("Error trying to send message:(chat:%s,text:%s,parse_mode:%s,disable_preview:%s,reply_keyboard:%s" %
                         (chat_id, text, parse_mode, disable_web_page_preview, keyboard))
