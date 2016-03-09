# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from microbot.models import Bot
from jinja2 import Template
import requests
from django.conf.urls import url
import json
import logging

logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class Request(models.Model):
    url_template = models.CharField(_('Url template'), max_length=255)
    GET, POST, PUT, DELETE = ("Get", "Post", "Put", "Delete")
    METHOD_CHOICES = (
        (GET, _("Get")),
        (POST, _("Post")),
        (PUT, _("Put")),
        (DELETE, _("Delete")),
    )
    method = models.CharField(_("Method"), max_length=128, default=GET, choices=METHOD_CHOICES)
    content_type = models.CharField(_('Content type'), max_length=255, null=True, blank=True)
    data = models.TextField(null=True, blank=True, verbose_name=_("Data of the request"))
    
    class Meta:
        verbose_name = _('Request')
        verbose_name_plural = _('Requests')

    def __str__(self):
        return "%s(%s)" % (self.method, self.url_template)
    
    def process(self, **context):
        url_template = Template(self.url_template)
        url = url_template.render(**context)
        logger.debug("Request %s generates url %s" % (self, url))
        if self.method == self.GET:
            r = requests.get(url)
        elif self.method == self.POST:
            headers = {'content_type': self.content_type}
            r = requests.post(url, json.loads(self.data), headers=headers)
        elif self.method == self.PUT:
            headers = {'content_type': self.content_type}
            r = requests.put(url, json.loads(self.data), headers=headers)
        else:
            r = requests.delete(url)
        return r


@python_2_unicode_compatible
class Handler(models.Model):
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="handlers")
    pattern = models.CharField(_('Pattern'), max_length=255)    
    request = models.OneToOneField(Request)
    response_text_template = models.TextField(verbose_name=_("Text response template"))
    response_keyboard_template = models.TextField(null=True, blank=True, verbose_name=_("Keyboard response template"))
    enabled = models.BooleanField(_('Enable'), default=True)
    
    class Meta:
        verbose_name = _('Handler')
        verbose_name_plural = _('Handlers')

    def __str__(self):
        return "%s" % self.pattern
    
    def urlpattern(self):
        return url(self.pattern, self.process)
    
    def process(self, bot, update, **url_context):
        r = self.request.process(**url_context)
        logger.debug("Handler %s get request %s" % (self, r))
        response_text_template = Template(self.response_text_template)
        try:
            response_context = r.json()
            if isinstance(response_context, list):
                response_context = {"list": response_context}
        except:
            response_context = {}
        context = {'url': url_context,
                   'response': response_context}
        response_text = response_text_template.render(**context)
        logger.debug("Handler %s generates text response %s" % (self, response_text))
        if self.response_keyboard_template:
            response_keyboard_template = Template(self.response_keyboard_template)
            response_keyboard = response_keyboard_template.render(**context)
        else:
            response_keyboard = None
        logger.debug("Handler %s generates keyboard response %s" % (self, response_keyboard))
        return response_text, response_keyboard
