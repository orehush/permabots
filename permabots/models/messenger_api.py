# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from permabots.models.base import PermabotsModel


@python_2_unicode_compatible
class MessengerMessage(PermabotsModel):
    bot = models.ForeignKey('MessengerBot', related_name='messages', verbose_name=_("Messenger Bot"))
    sender = models.CharField(_("Sender Id"), max_length=255)
    recipient = models.CharField(_("Recipient Id"), max_length=255)
    timestamp = models.DateTimeField(_('Timestamp'))
    MESSAGE, POSTBACK, DELIVERY = 'message', 'postback', 'delivery'

    TYPE_CHOICES = (
        (MESSAGE, _('Message')),
        (POSTBACK, _('Postback')),
        (DELIVERY, _('Delivery')),
    )
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    postback = models.CharField(_("PostBack"), null=True, blank=True, max_length=255)
    text = models.TextField(null=True, blank=True, verbose_name=_("Text"))

    class Meta:
        verbose_name = 'Messenger Message'
        verbose_name_plural = 'Messenger Messages'
        ordering = ['-timestamp', ]
        
    @property
    def is_message(self):
        return self.type == self.MESSAGE
    
    @property
    def is_postback(self):
        return self.type == self.POSTBACK
    
    @property
    def is_delivery(self):
        return self.type == self.DELIVERY
    
    @property
    def data(self):
        if self.is_message:
            return self.text
        elif self.is_postback:
            return self.postback
        else:
            return None

    def __str__(self):
        
        return "(%s,%s:%s)" % (self.id, self.type, self.data)
    
    def to_dict(self):
        message_dict = {'sender': self.sender,
                        'recipient': self.recipient,
                        'timestamp': self.timestamp,
                        }
        if self.is_message:
            message_dict.update({'text': self.text})
        elif self.is_postback:
            message_dict.update({'postback': self.postback})
        return message_dict    