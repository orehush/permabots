# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from permabots.models.base import PermabotsModel
from permabots.models import Bot
import logging

logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class EnvironmentVar(PermabotsModel):
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="env_vars", help_text=_("Bot which variable is attached."))
    key = models.CharField(_('Key'), max_length=255, help_text=_("Name of the variable"))
    value = models.CharField(_('Value'), max_length=255, help_text=_("Value of the variable"))      
    
    class Meta:
        verbose_name = _('Environment Var')
        verbose_name_plural = _('Environment Vars')

    def __str__(self):
        return "(%s, %s)" % (self.key, self.value)
    
    def as_json(self):
        return {self.key: self.value}