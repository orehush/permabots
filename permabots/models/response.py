# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import logging
from jinja2 import Template
from permabots.models.base import PermabotsModel
from permabots import validators

logger = logging.getLogger(__name__)

@python_2_unicode_compatible    
class Response(PermabotsModel):
    text_template = models.TextField(verbose_name=_("Text template"), validators=[validators.validate_template,
                                                                                  validators.validate_telegram_text_html],
                                     help_text=_("Template to generate text response. In jinja2 format. http://jinja.pocoo.org/"))
    keyboard_template = models.TextField(null=True, blank=True, verbose_name=_("Keyboard template"),
                                         validators=[validators.validate_template, validators.validate_telegram_keyboard],
                                         help_text=_("Template to generate keyboard response. In jinja2 format. http://jinja.pocoo.org/"))
    
    class Meta:
        verbose_name = _('Response')
        verbose_name_plural = _('Responses')

    def __str__(self):
        return "(text:%s, keyboard:%s)" % (self.text_template, self.keyboard_template)
    
    def process(self, **context):
        response_text_template = Template(self.text_template)
        response_text = response_text_template.render(**context)
        logger.debug("Response %s generates text  %s" % (self.text_template, response_text))
        if self.keyboard_template:
            response_keyboard_template = Template(self.keyboard_template)
            response_keyboard = response_keyboard_template.render(**context)
        else:
            response_keyboard = None
        logger.debug("Response %s generates keyboard  %s" % (self.keyboard_template, response_keyboard))
        return response_text, response_keyboard