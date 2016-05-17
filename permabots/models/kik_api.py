# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict
from permabots.models.base import PermabotsModel


@python_2_unicode_compatible
class KikUser(models.Model):
    username = models.CharField(_('User name'), max_length=255, primary_key=True)
    first_name = models.CharField(_('First name'), max_length=255, blank=True, null=True)
    last_name = models.CharField(_('Last name'), max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = _('Kik User')
        verbose_name_plural = _('Kik Users')

    def __str__(self):
        return "%s" % self.username

@python_2_unicode_compatible
class KikChat(models.Model):
    id = models.CharField(_('Id'), max_length=150, primary_key=True)
    participants = models.ManyToManyField(KikUser, verbose_name=_("Participants"), blank=True, related_name="chats") 
    
    class Meta:
        verbose_name = _('Kik Chat')
        verbose_name_plural = _('Kik Chats')

    def __str__(self):
        return "%s" % (self.id)

@python_2_unicode_compatible
class KikMessage(PermabotsModel):
    message_id = models.UUIDField(_('Id'), db_index=True)  # It is no unique?. Dont trust
    from_user = models.ForeignKey(KikUser, related_name='messages', verbose_name=_("User"))
    timestamp = models.DateTimeField(_('Timestamp'))
    chat = models.ForeignKey(KikChat, related_name='messages', verbose_name=_("Chat"))
    body = models.TextField(null=True, blank=True, verbose_name=_("Body"))
    #  TODO: complete fields with all message fields

    class Meta:
        verbose_name = 'Kik Message'
        verbose_name_plural = 'Kik Messages'
        ordering = ['-timestamp', ]

    def __str__(self):
        return "(%s,%s,%s)" % (self.message_id, self.chat, self.body or '(no text)')
    
    def to_dict(self):
        message_dict = model_to_dict(self, exclude=['from_user', 'chat', 'message_id'])
        message_dict.update({'id': self.message_id,
                             'from': self.from_user.username,
                             'chatId': self.chat.id,
                             'timestamp': self.timestamp,
                             'participants': [participant.username for participant in self.chat.participants.all()],
                             'type': "text",  # TODO: At the moment only text messages
                             })
        return message_dict