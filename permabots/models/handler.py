# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from permabots.models.base import PermabotsModel
from permabots.models import Bot, Response
from jinja2 import Template
import requests
from django.conf.urls import url
import json
import logging
from permabots import validators
from rest_framework.status import is_success
from permabots import caching 
from telegram import emoji
from six import iteritems, PY2

logger = logging.getLogger(__name__)


class AbstractParam(PermabotsModel):
    """
    Abstract parameter for :class:`Request <permabots.models.handler.Request>`
    """
    
    key = models.CharField(_('Key'), max_length=255, help_text=_("Name of the parameter"))
    value_template = models.CharField(_('Value template'), max_length=255, validators=[validators.validate_template], 
                                      help_text=_("Value template of the parameter. In jinja2 format. http://jinja.pocoo.org/"))
    
    class Meta:
        abstract = True
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
        
    def __str__(self):
        return "(%s, %s)" % (self.key, self.value_template)
    
    def process(self, **context):
        """
        Render value_template of the parameter using context.
        
        :param context: Processing context
        """
        value_template = Template(self.value_template)
        return value_template.render(**context) 

@python_2_unicode_compatible
class Request(PermabotsModel):
    """
    HTTP Request to perform some processing when handling a message
    """
    url_template = models.CharField(_('Url template'), max_length=255, validators=[validators.validate_template], 
                                    help_text=_("Url to request. A jinja2 template. http://jinja.pocoo.org/"))
    GET, POST, PUT, PATCH, DELETE = ("Get", "Post", "Put", "Patch", "Delete")
    METHOD_CHOICES = (
        (GET, _("Get")),
        (POST, _("Post")),
        (PUT, _("Put")),
        (DELETE, _("Delete")),
        (PATCH, _("Patch")),
    )
    method = models.CharField(_("Method"), max_length=128, default=GET, choices=METHOD_CHOICES, help_text=_("Define Http method for the request"))
    data = models.TextField(null=True, blank=True, verbose_name=_("Data of the request"), help_text=_("Set POST/PUT/PATCH data in json format"),
                            validators=[validators.validate_template])
    
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
        """
        Process handler request. Before executing requests render templates with context
        
        :param context: Processing context
        :returns: Requests response `<http://docs.python-requests.org/en/master/api/#requests.Response>` _.
        """
        url_template = Template(self.url_template)
        url = url_template.render(**context).replace(" ", "")
        logger.debug("Request %s generates url %s" % (self, url))        
        params = self._url_params(**context)
        logger.debug("Request %s generates params %s" % (self, params))
        headers = self._header_params(**context)
        logger.debug("Request %s generates header %s" % (self, headers))
        
        if self.data_required():
            data_template = Template(self.data)
            data = data_template.render(**context)
            logger.debug("Request %s generates data %s" % (self, data))
            r = self._get_method()(url, data=json.loads(data), headers=headers, params=params)
        else:
            r = self._get_method()(url, headers=headers, params=params)

        return r
    
class UrlParam(AbstractParam):
    """
    Url Parameter associated to the request.
    """
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="url_parameters",
                                help_text=_("Request which this Url Parameter is attached to"))
    
    class Meta:
        verbose_name = _("Url Parameter")
        verbose_name_plural = _("Url Parameters")
        
class HeaderParam(AbstractParam):
    """
    Header Parameter associated to the request
    """
    request = models.ForeignKey(Request, verbose_name=_('Request'), related_name="header_parameters",
                                help_text=_("Request which this Url Parameter is attached to"))
    
    class Meta:
        verbose_name = _("Header Parameter")
        verbose_name_plural = _("Header Parameters")

@python_2_unicode_compatible
class Handler(PermabotsModel):
    """
    Model to handler conversation message
    """
    bot = models.ForeignKey(Bot, verbose_name=_('Bot'), related_name="handlers",
                            help_text=_("Bot which Handler is attached to"))
    name = models.CharField(_('Name'), max_length=100, db_index=True, help_text=_("Name for the handler"))
    pattern = models.CharField(_('Pattern'), max_length=255, validators=[validators.validate_pattern], 
                               help_text=_("""Regular expression the Handler will be triggered. 
                               Using https://docs.python.org/2/library/re.html#regular-expression-syntax"""))   
    request = models.OneToOneField(Request, null=True, blank=True, help_text=_("Request the Handler processes"),
                                   on_delete=models.SET_NULL)
    response = models.OneToOneField(Response, help_text=_("Template the handler uses to generate response"))
    enabled = models.BooleanField(_('Enable'), default=True, help_text=_("Enable/disable handler"))
    source_states = models.ManyToManyField('State', verbose_name=_('Source States'), related_name='source_handlers', blank=True,
                                           help_text=_("Bot states the Handler needs to be to execute. Set none if any"))
    target_state = models.ForeignKey('State', verbose_name=_('Target State'), related_name='target_handlers', null=True, blank=True,
                                     help_text=_("This state will be set when handler ends processing"), on_delete=models.SET_NULL)
    priority = models.IntegerField(_('Priority'), default=0,
                                   help_text=_("Set priority execution. Higher value higher priority"))
    
    class Meta:
        verbose_name = _('Handler')
        verbose_name_plural = _('Handlers')
        ordering = ['-priority']

    def __str__(self):
        return "%s" % self.name
    
    def urlpattern(self):
        return url(self.pattern, self.process)
    
    def _create_emoji_context(self):
        context = {}
        for key, value in iteritems(emoji.Emoji.__dict__):
            if '__' not in key:
                if PY2:
                    value = value.decode('utf-8')
                context[key.lower().replace(" ", "_")] = value                    
        return context
                
    def process(self, bot, message, service, state_context, **pattern_context):
        """
        Process conversation message.
        
        1. Generates context
            * service: name of integration service
            * state_context: historic dict of previous contexts. identified by state
            * pattern: url pattern dict
            * env: dict of environment variables associated to this bot
            * message: provider message
            * emoji: dict of emojis  use named notation with underscores `<http://apps.timwhitlock.info/emoji/tables/unicode>` _.
            
        2. Process request (if required)
        
        3. Generates response. Text and Keyboard
        
        4. Prepare target_state and context for updating chat&state info
        
        :param bot: Bot the handler belongs to
        :type Bot: :class:`Bot <permabots.models.bot.Bot>`
        :param message: Message from provider
        :param service: Identity integration
        :type service: string
        :param state_context: Previous contexts
        :type state_context: dict
        :param pattern_context: Dict variables obtained from handler pattern regular expression.
        :type pattern_context: dict
        :returns: Text and keyboard response, new state for the chat and context used.
        """
        env = {}
        for env_var in caching.get_or_set_related(bot, 'env_vars'):
            env.update(env_var.as_json())
        context = {'service': service,
                   'state_context': state_context,
                   'pattern': pattern_context,
                   'env': env,
                   'message': message.to_dict(),
                   'emoji': self._create_emoji_context()}
        response_context = {}
        success = True
        if self.request:
            r = self.request.process(**context)
            logger.debug("Handler %s get request %s" % (self, r))        
            success = is_success(r.status_code)
            response_context['status'] = r.status_code
            try:
                response_context['data'] = r.json()
            except:
                response_context['data'] = {}
        context['response'] = response_context
        response_text, response_keyboard = self.response.process(**context)
        # update ChatState
        if self.target_state and success:
            context.pop('message', None)
            context.pop('env', None)
            context.pop('state_context', None)
            context.pop('service', None)
            context.pop('emoji', None)
            target_state = self.target_state
        else:
            target_state = None
            logger.warning("No target state for handler:%s for message %s" % 
                           (self, message))
        return response_text, response_keyboard, target_state, context