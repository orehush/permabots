# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import logging
from microbot.models.base import MicrobotModel
from microbot.models import Chat
import json

logger = logging.getLogger(__name__)

@python_2_unicode_compatible    
class State(MicrobotModel):    
    name = models.CharField(_('State name'), db_index=True, max_length=255, 
                            help_text=_("Set name to state which helps you to remember it."))
    bot = models.ForeignKey('Bot', verbose_name=_('Bot'), related_name='states',
                            help_text=_("Bot which state is attached to."))  
    
    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return "%s" % self.name
    
    
@python_2_unicode_compatible    
class ChatState(MicrobotModel):
    chat = models.OneToOneField(Chat, db_index=True, verbose_name=_('Chat'),
                                help_text=_("Chat identifier. Telegram API format."))
    state = models.ForeignKey(State, verbose_name=_('State'), related_name='chat',
                              help_text=_("State related to the chat."))
    context = models.TextField(verbose_name=_("Context"),
                               help_text=_("Context serialized to json when this state was set"), null=True, 
                               blank=True)

    class Meta:
        verbose_name = _('Chat State')
        verbose_name = _('Chats States')
        
    def __str__(self):
        return "(%s:%s)" % (str(self.chat.id), self.state.name)
    
    def _get_context(self):
        if self.context:
            return json.loads(self.context)
        return {}
    
    def _set_context(self, value):
        self.context = json.dumps(value)        
    
    ctx = property(_get_context, _set_context)