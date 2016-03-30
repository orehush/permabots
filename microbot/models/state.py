# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import logging
from microbot.models.base import MicrobotModel
from microbot.models import Chat

logger = logging.getLogger(__name__)

@python_2_unicode_compatible    
class State(MicrobotModel):    
    name = models.CharField(_('State name'), db_index=True, max_length=255)
    bot = models.ForeignKey('Bot', verbose_name=_('Bot'), related_name='states')  
    
    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return "%s" % self.name
    
    
@python_2_unicode_compatible    
class ChatState(MicrobotModel):
    chat = models.OneToOneField(Chat, db_index=True, verbose_name=_('Chat'))
    state = models.ForeignKey(State, verbose_name=_('State'), related_name='chat')

    class Meta:
        verbose_name = _('Chat State')
        verbose_name = _('Chats States')
        
    def __str__(self):
        return "(%s:%s)" % (str(self.chat.id), self.state.name)