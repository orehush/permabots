# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from microbot.models.base import MicrobotModel
from microbot.models import Bot, Response, ChatState
from jinja2 import Template
import requests
from django.conf.urls import url
import json
import logging
from microbot import validators

logger = logging.getLogger(__name__)


class AbstractParam(MicrobotModel):
    key = models.CharField(_('Key'), max_length=255, help_text=_("Set the name of the parameter"))
    value_template = models.CharField(_('Value template'), max_length=255, validators=[validators.validate_template], 
                                      help_text=_("Set the value of the parameter. A jinja2 template."))
    
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
class Request(MicrobotModel):
    url_template = models.CharField(_('Url template'), max_length=255, validators=[validators.validate_template], 
                                    help_text=_("Set the url to request. A jinja2 template."))
    GET, POST, PUT, PATCH, DELETE = ("Get", "Post", "Put", "Patch", "Delete")
    METHOD_CHOICES = (
        (GET, _("Get")),
        (POST, _("Post")),
        (PUT, _("Put")),
        (DELETE, _("Delete")),
        (PATCH, _("Patch")),
    )
    method = models.CharField(_("Method"), max_length=128, default=GET, choices=METHOD_CHOICES, help_text=_("Define Http method for the request"))
    data = models.TextField(null=True, blank=True, verbose_name=_("Data of the request"), help_text=_("Set POST/PUT/PATCH data in json format"))
    
    class Meta:
        verbose_name = _('Request')
        verbose_name_plural = _('Requests')

    def __str__(self):
        return "%s(%s)" % (self.method, self.url_template)
    
    def _get_method(self):
        method = {self.GET: requests.get,
                  self.POST: requests.post,
                  self.PUT: requests.put,
                  self.PATCH: requests.patch,
                  self.DELETE: requests.delete}
        try:
            return method[self.method]
        except KeyError:
            logger.error("Method %s not valid" % self.method)
            return method[self.GET]
    
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
    
    def data_required(self):
        return self.method != self.GET and self.method != self.DELETE
    
    def process(self, **context):
        url_template = Template(self.url_template)
        url = url_template.render(**context)
        logger.debug("Request %s generates url %s" % (self, url))        
        params = self._url_params(**context)
        logger.debug("Request %s generates params %s" % (self, params))
        headers = self._header_params(**context)
        logger.debug("Request %s generates header %s" % (self, headers))
        
        if self.data_required():
            data_template = Template(self.data)
            data = data_template.render(**context)
            r = self._get_method()(url, data=json.loads(data), headers=headers, params=params)
        else:
            r = self._get_method()(url, headers=headers, params=params)

        return r
    
class UrlParam(AbstractParam):
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="url_parameters",
                                help_text=_("Request which this Url Parameter is attached to."))
    
    class Meta:
        verbose_name = _("Url Parameter")
        verbose_name_plural = _("Url Parameters")
        
class HeaderParam(AbstractParam):
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="header_parameters",
                                help_text=_("Request which this Url Parameter is attached to."))
    
    class Meta:
        verbose_name = _("Header Parameter")
        verbose_name_plural = _("Header Parameters")

@python_2_unicode_compatible
class Handler(MicrobotModel):
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="handlers",
                            help_text=_("Bot which Handler is attached to."))
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Set a name for the handler which helps you to remember it."))
    pattern = models.CharField(_('Pattern'), max_length=255, validators=[validators.validate_pattern], 
                               help_text=_("Regular expression the Handler will be triggered."))   
    request = models.OneToOneField(Request, null=True, blank=True, help_text=_("Request the Handler processes."),
                                   on_delete=models.SET_NULL)
    response = models.OneToOneField(Response, help_text=_("Set how Handler responses."))
    enabled = models.BooleanField(_('Enable'), default=True, help_text=_("enable/disable Handler."))
    source_states = models.ManyToManyField('State', verbose_name=_('Source States'), related_name='source_handlers', blank=True,
                                           help_text=_("Bot states the Handler executes. Set none if any."))
    target_state = models.ForeignKey('State', verbose_name=_('Target State'), related_name='target_handlers', null=True, blank=True,
                                     help_text=_("Bot state it is set when Handler finishes."))
    priority = models.IntegerField(_('Priority'), default=0,
                                   help_text=_("Set priority execution. Higher value higher priority."))
    
    class Meta:
        verbose_name = _('Handler')
        verbose_name_plural = _('Handlers')
        ordering = ['-priority']

    def __str__(self):
        return "%s" % self.name
    
    def urlpattern(self):
        return url(self.pattern, self.process)
    
    def process(self, bot, update, state_context, **url_context):
        env = {}
        for env_var in bot.env_vars.all():
            env.update(env_var.as_json())
        context = {'state_context': state_context,
                   'url': url_context,
                   'env': env,
                   'update': update.to_dict()}
        if not self.request:
            response_context = {}
        else:
            r = self.request.process(**context)
            logger.debug("Handler %s get request %s" % (self, r))        
            try:
                response_context = r.json()
                if isinstance(response_context, list):
                    response_context = {"list": response_context}
            except:
                response_context = {}
        context['response'] = response_context
        response_text, response_keyboard = self.response.process(**context)
        # update ChatState
        if self.target_state:
            context.pop('update', None)
            context.pop('env', None)
            try:
                chat_state = ChatState.objects.get(chat=update.message.chat)
            except ChatState.DoesNotExist:
                logger.warning("Chat state for update chat %s not exists" % 
                               (update.message.chat.id))
                ChatState.objects.create(chat=update.message.chat,
                                         state=self.target_state,
                                         ctx=context)
            else:
                if chat_state.state != self.target_state:
                    chat_state.state = self.target_state
                    chat_state.ctx = context
                    chat_state.save()
                    logger.debug("Chat state updated:%s for update %s with %s" % 
                                 (self.target_state, update, context))
                else:
                    logger.debug("ChateState stays in %s" % self.target_state)
        else:
            logger.warning("No target state for handler:%s for update %s" % 
                           (self, update))
            
        return response_text, response_keyboard