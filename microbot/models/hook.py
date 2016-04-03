# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from microbot.models.base import MicrobotModel
from microbot.models import Response, Bot
import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
import shortuuid

logger = logging.getLogger(__name__)


@python_2_unicode_compatible    
class Hook(MicrobotModel):
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="hooks",
                            help_text=_("Bot which Hook is attached."))
    name = models.CharField(_('Name'), max_length=100, db_index=True,
                            help_text=_("Set a name for the hook which helps you to remember."))
    key = models.CharField(max_length=30, db_index=True, editable=False, unique=True,
                           help_text=_("Key generated to complete the Hoom url."))
    response = models.OneToOneField(Response, verbose_name=_('Response'),
                                    help_text=_("Set how Hook responses."))
    enabled = models.BooleanField(_('Enable'), default=True, help_text="enable/disbale Hook.")
   
    class Meta:
        verbose_name = _('Hook')
        verbose_name_plural = _('Hooks')
        
    def __str__(self):
        return "(%s, %s)" % (self.name, self.key)           
    
    def generate_key(self):
        return shortuuid.uuid()
    
    def process(self, bot, data):
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
class Recipient(MicrobotModel):
    chat_id = models.BigIntegerField(_('Chat id'), db_index=True, help_text=_("Chat identifier provided by Telegram API."))
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Set name for recipient which helps you to remember it."))
    hook = models.ForeignKey(Hook, verbose_name=_('Recipient'), related_name="recipients",
                             help_text=_("Hook which recipient is attached to."))

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')      
        
    def __str__(self):
        return "%s" % self.chat_id    