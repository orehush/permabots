# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)

@python_2_unicode_compatible    
class Response(models.Model):
    text_template = models.TextField(verbose_name=_("Text template"))
    keyboard_template = models.TextField(null=True, blank=True, verbose_name=_("Keyboard template"))
    
    class Meta:
        verbose_name = _('Response')
        verbose_name_plural = _('Response')

    def __str__(self):
        return "(text:%s, keyboard:%s)" % (self.text_template, self.keyboard_template) 