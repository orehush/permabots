# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from permabots.models.base import PermabotsModel
from permabots.models import Response, Bot
import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
import shortuuid

logger = logging.getLogger(__name__)


@python_2_unicode_compatible    
class Hook(PermabotsModel):
    """
    Notification Hook representation.
    
    The webhook url is generated with the key.
    """
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="hooks",
                            help_text=_("Bot which Hook is attached"))
    name = models.CharField(_('Name'), max_length=100, db_index=True,
                            help_text=_("Name of the hook"))
    key = models.CharField(max_length=30, db_index=True, editable=False, unique=True,
                           help_text=_("Key generated to complete the Hook url. http://permabots.com/process/hook/{{key}}"))
    response = models.OneToOneField(Response, verbose_name=_('Response'),
                                    help_text=_("Template the hook uses to generate the response"))
    enabled = models.BooleanField(_('Enable'), default=True, help_text="Enable/disable hook")
   
    class Meta:
        verbose_name = _('Hook')
        verbose_name_plural = _('Hooks')
        
    def __str__(self):
        return "(%s, %s)" % (self.name, self.key)           
    
    def generate_key(self):
        return shortuuid.uuid()
    
    def process(self, bot, data):
        """
        Notification hook processing generating a response.
        
        :param bot: Bot receiving the hook
        :type Bot: :class:`Bot <permabots.models.bot.Bot>`
        :param data: JSON data from hook POST
        :type: JSON
        """
        env = {}
        for env_var in bot.env_vars.all():
            env.update(env_var.as_json())
        context = {'env': env,
                   'data': data}
        response_text, response_keyboard = self.response.process(**context)
        return response_text, response_keyboard   
    
@receiver(pre_save, sender=Hook)
def set_key(sender, instance, **kwargs):
    if not instance.key:
        instance.key = instance.generate_key()
    
@python_2_unicode_compatible 
class TelegramRecipient(PermabotsModel):
    chat_id = models.BigIntegerField(_('Chat id'), db_index=True, help_text=_("Chat identifier provided by Telegram API"))
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Name of recipient"))
    hook = models.ForeignKey(Hook, verbose_name=_('Hook'), related_name="telegram_recipients",
                             help_text=_("Hook which recipient is attached to"))

    class Meta:
        verbose_name = _('Telegram Recipient')
        verbose_name_plural = _('Telegram Recipients')      
        
    def __str__(self):
        return "(%s, %s)" % (self.chat_id, self.name)
    
@python_2_unicode_compatible 
class KikRecipient(PermabotsModel):
    chat_id = models.CharField(_('Chat Id'), max_length=150, db_index=True, help_text=_("Chat identifier provided by Kik API"))
    username = models.CharField(_('User name'), max_length=255, db_index=True)
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Name of recipient"))
    hook = models.ForeignKey(Hook, verbose_name=_('Hook'), related_name="kik_recipients",
                             help_text=_("Hook which recipient is attached to"))

    class Meta:
        verbose_name = _('Kik Recipient')
        verbose_name_plural = _('Kik Recipients')      
        
    def __str__(self):
        return "(%s, %s, %s)" % (self.name, self.chat_id, self.username)    
    
@python_2_unicode_compatible 
class MessengerRecipient(PermabotsModel):
    chat_id = models.CharField(_('Chat Id'), max_length=150, db_index=True, help_text=_("Chat identifier provided by Messenger API"))
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Name of recipient"))
    hook = models.ForeignKey(Hook, verbose_name=_('Hook'), related_name="messenger_recipients",
                             help_text=_("Hook which recipient is attached to"))

    class Meta:
        verbose_name = _('Messenger Recipient')
        verbose_name_plural = _('Messenger Recipients')      
        
    def __str__(self):
        return "(%s, %s, %s)" % (self.name, self.chat_id)  