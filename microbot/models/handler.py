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


class AbstractParam(models.Model):
    key = models.CharField(_('Key'), max_length=255)
    value_template = models.CharField(_('Value template'), max_length=255)
    
    class Meta:
        abstract = True
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
        
    def __str__(self):
        return "(%s, %s)" % (self.key, self.value_template)
    
    def process(self, **context):
        value_template = Template(self.value_template)
        return value_template.render(**context) 

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
    data = models.TextField(null=True, blank=True, verbose_name=_("Data of the request"))
    
    class Meta:
        verbose_name = _('Request')
        verbose_name_plural = _('Requests')

    def __str__(self):
        return "%s(%s)" % (self.method, self.url_template)
    
    def _url_params(self, **context):
        params = {}
        for param in self.url_parameters.all():
            params[param.key] = param.process(**context)
        return params
    
    def _header_params(self, **context):
        headers = {}
        for header in self.header_parameters.all():
            headers[header.key] = header.process(**context)
        return headers
    
    def process(self, **context):
        url_template = Template(self.url_template)
        url = url_template.render(**context)
        logger.debug("Request %s generates url %s" % (self, url))        
        params = self._url_params(**context)
        logger.debug("Request %s generates params %s" % (self, params))
        headers = self._header_params(**context)
        logger.debug("Request %s generates header %s" % (self, headers))
        
        if self.method == self.GET:
            r = requests.get(url, headers=headers, params=params)
        elif self.method == self.POST:
            r = requests.post(url, data=json.loads(self.data), headers=headers, params=params)
        elif self.method == self.PUT:
            r = requests.put(url, data=json.loads(self.data), headers=headers, params=params)
        else:
            r = requests.delete(url, headers=headers, params=params)
        return r
    
class UrlParam(AbstractParam):
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="url_parameters")
    
    class Meta:
        verbose_name = _("Url Parameter")
        verbose_name_plural = _("Url Parameters")
        
class HeaderParam(AbstractParam):
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="header_parameters")
    
    class Meta:
        verbose_name = _("Header Parameter")
        verbose_name_plural = _("Header Parameters")   


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
        env = {}
        for env_var in bot.env_vars.all():
            env.update(env_var.as_json())
        context = {'url': url_context,
                   'env': env}
        r = self.request.process(**context)
        logger.debug("Handler %s get request %s" % (self, r))
        response_text_template = Template(self.response_text_template)
        try:
            response_context = r.json()
            if isinstance(response_context, list):
                response_context = {"list": response_context}
        except:
            response_context = {}
        context['response'] = response_context
        response_text = response_text_template.render(**context)
        logger.debug("Handler %s generates text response %s" % (self, response_text))
        if self.response_keyboard_template:
            response_keyboard_template = Template(self.response_keyboard_template)
            response_keyboard = response_keyboard_template.render(**context)
        else:
            response_keyboard = None
        logger.debug("Handler %s generates keyboard response %s" % (self, response_keyboard))
        return response_text, response_keyboard
