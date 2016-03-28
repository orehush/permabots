#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, EnvironmentVar, Handler, Hook, Recipient
from microbot.test import testcases, factories
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from microbot.views import BotDetail, EnvironmentVarDetail, HandlerDetail, HookDetail, RecipientDetail,\
    UrlParameterDetail, HeaderParameterDetail
from django.conf import settings
from django.apps import apps
import json
from microbot.models.handler import HeaderParam, UrlParam
ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))

class BaseTestAPI(testcases.BaseTestBot):
    
    def setUp(self):
        super(BaseTestAPI, self).setUp()
        self.api = '/microbot/api'
        self.mytoken = '204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc'
        self.mytoken2 = '190880460:AAELDdTxhhfPbtPRyC59qPaVF5VBX4VGVes'
        
    def _test_get_list_ok(self, url):
        response = self.client.get(url, HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()
    
    def _test_get_list_not_auth(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def _test_post_list_ok(self, url, model, data):
        model.objects.all().delete()
        response = self.client.post(url,
                                    data=json.dumps(data), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()
    
    def _test_post_list_not_auth(self, url, data):
        response = self.client.post(url, 
                                    data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def _test_get_detail_ok(self, url):
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()
    
    def _test_get_detail_not_auth(self, url):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def _test_get_detail_not_found(self, url):
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_put_detail_ok(self, url, data, view, *args):
        factory = APIRequestFactory()
        request = factory.put(url, data, format="json")
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _test_put_detail_not_auth(self, url, data, view, *args):
        factory = APIRequestFactory()
        request = factory.put(url, data, format="json")
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def _test_put_detail_not_found(self, url, data, view, *args):
        factory = APIRequestFactory()
        request = factory.put(url, data, format="json")
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_delete_detail_ok(self, url, view, *args):
        factory = APIRequestFactory()
        request = factory.delete(url)
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def _test_delete_detail_not_auth(self, url, view, *args):
        factory = APIRequestFactory()
        request = factory.delete(url)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def _test_delete_detail_not_found(self, url, view, *args):
        factory = APIRequestFactory()
        request = factory.delete(url)
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_get_detail_from_other_bot(self, func_url, *args):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        response = self.client.get(func_url(new_bot.pk, *args),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_put_detail_from_other_bot(self, func_url, data, view, *args):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.put(func_url(new_bot.pk), data, format="json")
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, new_bot.pk, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_delete_detail_from_other_bot(self, func_url, view, *args):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.delete(func_url(new_bot.pk))
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, new_bot.pk, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
        
class TestBotAPI(BaseTestAPI):
    
    def assertBot(self, token, enabled, username, first_name, last_name, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(bot.token, token)
        self.assertEqual(bot.enabled, enabled)
        self.assertEqual(bot.user_api.username, username)
        self.assertEqual(bot.user_api.first_name, first_name)
        self.assertEqual(bot.user_api.last_name, last_name)
        
    def _bot_list_url(self):
        return '%s/bots/' % self.api
        
    def _bot_detail_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/' % (self.api, bot_pk)
    
    def test_get_bots_ok(self):
        data = self._test_get_list_ok(self._bot_list_url())
        self.assertBot(data[0]['token'], data[0]['enabled'], data[0]['info']['username'], 
                       data[0]['info']['first_name'], data[0]['info']['last_name'])
        
    def test_get_bots_not_auth(self):
        self._test_get_list_not_auth(self._bot_list_url())
        
    def test_post_bots_ok(self):
        self._test_post_list_ok(self._bot_list_url(), Bot, {'token': self.mytoken, 'enabled': 'True'})
        new_bot = Bot.objects.get(token=self.mytoken)
        self.assertEqual(new_bot.token, self.mytoken)
        self.assertTrue(new_bot.enabled)
        
    def test_post_bots_not_auth(self):
        self._test_post_list_not_auth(self._bot_list_url(), {'token': self.mytoken, 'enabled': 'True'})
        
    def test_get_bot_ok(self):
        data = self._test_get_detail_ok(self._bot_detail_url())
        self.assertBot(data['token'], data['enabled'], data['info']['username'],
                       
                       data['info']['first_name'], data['info']['last_name'])
        
    def test_get_bot_not_auth(self):
        self._test_get_detail_not_auth(self._bot_detail_url())
        
    def test_get_bot_not_found(self):
        self._test_get_detail_not_found(self._bot_detail_url(12))
        
    def test_put_bot_ok(self):
        self._test_put_detail_ok(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, self.bot.pk)
        self.assertFalse(Bot.objects.get(pk=self.bot.pk).enabled)
        
    def test_put_bot_not_auth(self):
        self._test_put_detail_not_auth(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, self.bot.pk)
        
    def test_put_bot_not_found(self):
        self._test_put_detail_not_found(self._bot_detail_url(12), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, 12)
          
    def test_delete_bot_ok(self):
        self._test_delete_detail_ok(self._bot_detail_url(), BotDetail, self.bot.pk)
        self.assertEqual(Bot.objects.count(), 0)
        
    def test_delete_bot_not_auth(self):
        self._test_delete_detail_not_auth(self._bot_detail_url(), BotDetail, self.bot.pk)
        
    def test_delete_bot_not_found(self):
        self._test_delete_detail_not_found(self._bot_detail_url(12), BotDetail, 12)       

        
class TestEnvironmentVarAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestEnvironmentVarAPI, self).setUp()
        self.key = "shop"
        self.value = "myebookshop"
        self.env_var = EnvironmentVar.objects.create(bot=self.bot,
                                                     key=self.key, 
                                                     value=self.value)
        
    def _env_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/env/' % (self.api, bot_pk)
    
    def _env_detail_url(self, bot_pk=None, env_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not env_pk:
            env_pk = self.env_var.pk
        return '%s/bots/%s/env/%s/' % (self.api, bot_pk, env_pk)
    
    def assertEnvVar(self, key, value, env_var=None):
        if not env_var:
            env_var = self.env_var
        self.assertEqual(env_var.key, key)
        self.assertEqual(env_var.value, value)
        
    def test_get_env_vars_ok(self):
        data = self._test_get_list_ok(self._env_list_url())
        self.assertEnvVar(data[0]['key'], data[0]['value'])
        
    def test_get_env_vars_not_auth(self):
        self._test_get_list_not_auth(self._env_list_url())
        
    def test_post_env_vars_ok(self):
        self._test_post_list_ok(self._env_list_url(), EnvironmentVar, {'key': self.key, 'value': self.value})
        new_env_var = EnvironmentVar.objects.filter(bot=self.bot)[0]
        self.assertEnvVar(self.key, self.value, new_env_var)
        
    def test_post_env_vars_not_auth(self):
        self._test_post_list_not_auth(self._env_list_url(), {'key': self.key, 'value': self.value})
                
    def test_get_env_var_ok(self):
        data = self._test_get_detail_ok(self._env_detail_url())
        self.assertEnvVar(data['key'], data['value'])
        
    def test_get_env_var_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._env_detail_url)
        
    def test_get_env_var_not_auth(self):
        self._test_get_detail_not_auth(self._env_detail_url())
        
    def test_get_env_var_not_found(self):
        self._test_get_detail_not_found(self._env_detail_url(env_pk=12))
        
    def test_put_env_var_ok(self):
        self._test_put_detail_ok(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        self.assertEqual(EnvironmentVar.objects.get(pk=self.env_var.pk).value, 'new_value')
        
    def test_put_env_var_from_other_bot(self):
        self._test_put_detail_from_other_bot(self._env_detail_url, {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.env_var.pk)
        
    def test_put_env_var_not_auth(self):
        self._test_put_detail_not_auth(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail,
                                       self.bot.pk, self.env_var.pk)
        
    def test_put_env_var_not_found(self):
        self._test_put_detail_not_found(self._env_detail_url(env_pk=12), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.bot.pk, 12)
          
    def test_delete_env_var_ok(self):
        self._test_delete_detail_ok(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_env_var_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._env_detail_url, EnvironmentVarDetail, self.env_var.pk)
        
    def test_delete_env_var_not_auth(self):
        self._test_delete_detail_not_auth(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
       
    def test_delete_env_var_not_found(self):
        self._test_delete_detail_not_found(self._env_detail_url(env_pk=12), EnvironmentVarDetail, self.bot.pk, 12)
        
class TestHandlerAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.url_param = factories.UrlParamFactory(request=self.handler.request)
        self.header_param = factories.HeaderParamFactory(request=self.handler.request)
        
    def _handler_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/handlers/' % (self.api, bot_pk)
    
    def _handler_detail_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/' % (self.api, bot_pk, handler_pk)
    
    def _handler_url_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/urlparams/' % (self.api, bot_pk, handler_pk)    
    
    def _handler_header_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/headerparams/' % (self.api, bot_pk, handler_pk)            
    
    def assertHandler(self, name, pattern, response_text_template, response_keyboard_template, enabled, handler=None):
        if not handler:
            handler = self.handler
        self.assertEqual(handler.name, name)
        self.assertEqual(handler.pattern, pattern)
        self.assertEqual(handler.response.text_template, response_text_template)
        self.assertEqual(handler.response.keyboard_template, response_keyboard_template)
        self.assertEqual(handler.enabled, enabled)
        
    def assertUrlParam(self, key, value_template, url_param=None):
        if not url_param:
            url_param = self.url_param
        self.assertEqual(url_param.key, key)
        self.assertEqual(url_param.value_template, value_template)

    def assertHeaderParam(self, key, value_template, header_param=None):
        if not header_param:
            header_param = self.header_param
        self.assertEqual(header_param.key, key)
        self.assertEqual(header_param.value_template, value_template)
        
    def test_get_handlers_ok(self):
        data = self._test_get_list_ok(self._handler_list_url())
        self.assertHandler(data[0]['name'], data[0]['pattern'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                           data[0]['enabled'])
        
    def test_get_handlers_not_auth(self):
        self._test_get_list_not_auth(self._handler_list_url())
        
    def test_post_handlers_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False, 'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                              'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                  'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                              'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                     'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                              }                                                                         
                }
        self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(self.handler.name, self.handler.pattern, self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, new_handler)
        
    def test_post_handlers_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False,
                'request': self.handler.request}
        self._test_post_list_not_auth(self._handler_list_url(), data)
        
    def test_get_handler_ok(self):
        data = self._test_get_detail_ok(self._handler_detail_url())
        self.assertHandler(data['name'], data['pattern'], data['response']['text_template'], data['response']['keyboard_template'], data['enabled'])
        
    def test_get_handler_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_detail_url)
        
    def test_get_handler_not_auth(self):
        self._test_get_detail_not_auth(self._handler_detail_url())
        
    def test_get_handler_not_found(self):
        self._test_get_detail_not_found(self._handler_detail_url(handler_pk=12))
        
    def test_put_handler_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            }
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_from_other_bot(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_from_other_bot(self._handler_detail_url, data, HandlerDetail, self.handler.pk)
        
    def test_put_handler_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_auth(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_put_handler_not_found(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_found(self._handler_detail_url(handler_pk=12), data, HandlerDetail, self.bot.pk, 12)
          
    def test_delete_handler_ok(self):
        self._test_delete_detail_ok(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_handler_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_detail_url, HandlerDetail, self.handler.pk)
        
    def test_delete_handler_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_delete_handler_not_found(self):
        self._test_delete_detail_not_found(self._handler_detail_url(handler_pk=12), HandlerDetail, self.bot.pk, 12)

        
class TestHandlerRequestParamsAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerRequestParamsAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.url_param = factories.UrlParamFactory(request=self.handler.request)
        self.header_param = factories.HeaderParamFactory(request=self.handler.request)
    
    def _handler_url_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/urlparams/' % (self.api, bot_pk, handler_pk)
    
    def _handler_url_param_detail_url(self, bot_pk=None, handler_pk=None, url_param_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not url_param_pk:
            url_param_pk = self.url_param.pk
        return '%s/bots/%s/handlers/%s/urlparams/%s/' % (self.api, bot_pk, handler_pk, url_param_pk)    
    
    def _handler_header_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/headerparams/' % (self.api, bot_pk, handler_pk)     
    
    def _handler_header_param_detail_url(self, bot_pk=None, handler_pk=None, header_param_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not header_param_pk:
            header_param_pk = self.header_param.pk
        return '%s/bots/%s/handlers/%s/headerparams/%s/' % (self.api, bot_pk, handler_pk, header_param_pk)            
        
    def assertUrlParam(self, key, value_template, url_param=None):
        if not url_param:
            url_param = self.url_param
        self.assertEqual(url_param.key, key)
        self.assertEqual(url_param.value_template, value_template)

    def assertHeaderParam(self, key, value_template, header_param=None):
        if not header_param:
            header_param = self.header_param
        self.assertEqual(header_param.key, key)
        self.assertEqual(header_param.value_template, value_template)
        
    def test_get_handler_url_params_ok(self):
        data = self._test_get_list_ok(self._handler_url_param_list_url())
        self.assertUrlParam(data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_url_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_url_param_list_url())
        
    def test_post_handler_url_params_ok(self):
        data = {'key': self.handler.request.url_parameters.all()[0].key,
                'value_template': self.handler.request.url_parameters.all()[0].value_template}                         
        self._test_post_list_ok(self._handler_url_param_list_url(), UrlParam, data)
        new_url_param = UrlParam.objects.filter(request=self.handler.request)[0]
        self.assertUrlParam(self.url_param.key, self.url_param.value_template, new_url_param)
        
    def test_post_handler_url_params_not_auth(self):
        data = {'key': self.url_param.key,
                'value_template': self.url_param.value_template}
        self._test_post_list_not_auth(self._handler_url_param_list_url(), data)
            
    def test_get_handler_url_param_ok(self):
        data = self._test_get_detail_ok(self._handler_url_param_detail_url())
        self.assertUrlParam(data['key'], data['value_template'])
        
    def test_get_handler_url_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_url_param_detail_url)
        
    def test_get_handler_url_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_url_param_detail_url())
        
    def test_get_handler_url_param_not_found(self):
        self._test_get_detail_not_found(self._handler_url_param_detail_url(url_param_pk=12))
        
    def test_put_handler_url_param_ok(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_ok(self._handler_url_param_detail_url(), data, UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        self.assertEqual(UrlParam.objects.get(key=self.url_param.key).value_template, 'new_url_param_value')
        
    def test_put_handler_url_param_from_other_bot(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_from_other_bot(self._handler_url_param_detail_url, data, UrlParameterDetail, self.handler.pk, self.url_param.pk)
        
    def test_put_handler_url_param_not_auth(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_not_auth(self._handler_url_param_detail_url(), data, UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        
    def test_put_handler_url_param_not_found(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_not_found(self._handler_url_param_detail_url(url_param_pk=12), data, UrlParameterDetail, self.bot.pk, self.handler.pk, 12)
          
    def test_delete_handler_url_param_ok(self):
        self._test_delete_detail_ok(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        self.assertEqual(UrlParam.objects.count(), 0)
        
    def test_delete_handler_url_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_url_param_detail_url, UrlParameterDetail, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_url_param_detail_url(url_param_pk=12), UrlParameterDetail, self.bot.pk, self.handler.pk, 12)
        
    def test_get_handler_header_params_ok(self):
        data = self._test_get_list_ok(self._handler_header_param_list_url())
        self.assertHeaderParam(data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_header_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_header_param_list_url())
        
    def test_post_handler_header_params_ok(self):
        data = {'key': self.handler.request.header_parameters.all()[0].key,
                'value_template': self.handler.request.header_parameters.all()[0].value_template}                         
        self._test_post_list_ok(self._handler_header_param_list_url(), HeaderParam, data)
        new_header_param = HeaderParam.objects.filter(request=self.handler.request)[0]
        self.assertHeaderParam(self.header_param.key, self.header_param.value_template, new_header_param)
        
    def test_post_handler_header_params_not_auth(self):
        data = {'key': self.header_param.key,
                'value_template': self.header_param.value_template}
        self._test_post_list_not_auth(self._handler_header_param_list_url(), data)
        
    def test_get_handler_header_param_ok(self):
        data = self._test_get_detail_ok(self._handler_header_param_detail_url())
        self.assertHeaderParam(data['key'], data['value_template'])
        
    def test_get_handler_header_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_header_param_detail_url)
        
    def test_get_handler_header_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_header_param_detail_url())
        
    def test_get_handler_header_param_not_found(self):
        self._test_get_detail_not_found(self._handler_header_param_detail_url(header_param_pk=12))
        
    def test_put_handler_header_param_ok(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_ok(self._handler_header_param_detail_url(), data, HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        self.assertEqual(HeaderParam.objects.get(key=self.url_param.key).value_template, 'new_header_param_value')
        
    def test_put_handler_header_param_from_other_bot(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_from_other_bot(self._handler_header_param_detail_url, data, HeaderParameterDetail, self.handler.pk, self.header_param.pk)
        
    def test_put_handler_header_param_not_auth(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_not_auth(self._handler_header_param_detail_url(), data, HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        
    def test_put_handler_header_param_not_found(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_not_found(self._handler_header_param_detail_url(header_param_pk=12), data, 
                                        HeaderParameterDetail, self.bot.pk, self.handler.pk, 12)
          
    def test_delete_handler_header_param_ok(self):
        self._test_delete_detail_ok(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        self.assertEqual(HeaderParam.objects.count(), 0)
        
    def test_delete_handler_header_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_header_param_detail_url, HeaderParameterDetail, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_header_param_detail_url(header_param_pk=12), HeaderParameterDetail, self.bot.pk, self.handler.pk, 12)
    
class TestHookAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.RecipientFactory(hook=self.hook)
        
    def _hook_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/hooks/' % (self.api, bot_pk)
    
    def _hook_detail_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/' % (self.api, bot_pk, hook_pk)

    def assertHook(self, name, response_text_template, response_keyboard_template, enabled, recipients, hook=None):
        if not hook:
            hook = self.hook
        self.assertEqual(hook.name, name)
        self.assertEqual(hook.response.text_template, response_text_template)
        self.assertEqual(hook.response.keyboard_template, response_keyboard_template)
        self.assertEqual(hook.enabled, enabled)
        self.assertEqual(hook.recipients.count(), len(recipients))
        # check recipients
        for recipient in recipients:
            self.assertEqual(Recipient.objects.get(chat_id=recipient['chat_id']).chat_id, recipient['chat_id'])
            self.assertEqual(Recipient.objects.get(chat_id=recipient['chat_id']).name, recipient['name'])
        
    def test_get_hooks_ok(self):
        data = self._test_get_list_ok(self._hook_list_url())
        self.assertHook(data[0]['name'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                        data[0]['enabled'], data[0]['recipients'])
        
    def test_get_hooks_not_auth(self):
        self._test_get_list_not_auth(self._hook_list_url())
        
    def test_post_hooks_ok(self):
        data = {'name': self.hook.name, 'response': {'text_template': self.hook.response.text_template,
                                                     'keyboard_template': self.hook.response.keyboard_template},
                'enabled': False, 'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]
                }
        recipients = [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]                                   
        self._test_post_list_ok(self._hook_list_url(), Hook, data)
        new_hook = Hook.objects.filter(bot=self.bot)[0]
        self.assertHook(self.hook.name, self.hook.response.text_template, self.hook.response.keyboard_template,
                        False, recipients, hook=new_hook)
        
    def test_post_hooks_not_auth(self):
        data = {'name': self.hook.name, 'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]}
        self._test_post_list_not_auth(self._hook_list_url(), data)
        
    def test_get_hook_ok(self):
        data = self._test_get_detail_ok(self._hook_detail_url())
        self.assertHook(data['name'], data['response']['text_template'], data['response']['keyboard_template'], data['enabled'],
                        data['recipients'])
        
    def test_get_hook_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_detail_url)
        
    def test_get_hook_not_auth(self):
        self._test_get_detail_not_auth(self._hook_detail_url())
        
    def test_get_hook_not_found(self):
        self._test_get_detail_not_found(self._hook_detail_url(hook_pk=12))
        
    def test_put_hook_ok(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                             'keyboard_template': self.hook.response.keyboard_template}, 
                'enabled': False, 'name': self.hook.name,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]
                }
        self._test_put_detail_ok(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        self.assertEqual(Hook.objects.get(pk=self.hook.pk).enabled, False)
        
    def test_put_hook_from_other_bot(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                             'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]
                }
        self._test_put_detail_from_other_bot(self._hook_detail_url, data, HookDetail, self.hook.pk)
        
    def test_put_hook_not_auth(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]
                }
        self._test_put_detail_not_auth(self._hook_detail_url(), data, HandlerDetail, self.bot.pk, self.hook.pk)
        
    def test_put_hook_not_found(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]
                }
        self._test_put_detail_not_found(self._hook_detail_url(hook_pk=12), data, HookDetail, self.bot.pk, 12)
          
    def test_delete_hook_ok(self):
        self._test_delete_detail_ok(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_detail_url, HookDetail, self.hook.pk)
        
    def test_delete_hook_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_not_found(self):
        self._test_delete_detail_not_found(self._hook_detail_url(hook_pk=12), HookDetail, self.bot.pk, 12)


class TestHookRecipientAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookRecipientAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.RecipientFactory(hook=self.hook)
        
    def _hook_recipient_list_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/recipients/' % (self.api, bot_pk, hook_pk)
    
    def _hook_recipient_detail_url(self, bot_pk=None, hook_pk=None, recipient_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        if not recipient_pk:
            recipient_pk = self.hook.recipients.all()[0].pk
        return '%s/bots/%s/hooks/%s/recipients/%s/' % (self.api, bot_pk, hook_pk, recipient_pk)
    
    def assertRecipient(self, chat_id, name, recipient=None):
        if not recipient:
            recipient = self.hook.recipients.all()[0]
        self.assertEqual(recipient.chat_id, chat_id)
        self.assertEqual(recipient.name, name)

    def test_get_hook_recipients_ok(self):
        data = self._test_get_list_ok(self._hook_recipient_list_url())
        self.assertRecipient(data[0]['chat_id'], data[0]['name'])
        
    def test_get_hook_recipients_not_auth(self):
        self._test_get_list_not_auth(self._hook_recipient_list_url())
        
    def test_post_hook_recipient_ok(self):
        data = {'chat_id': self.hook.recipients.all()[0].chat_id, 'name': self.hook.recipients.all()[0].name}                              
        self._test_post_list_ok(self._hook_recipient_list_url(), Recipient, data)
        new_recipient = Recipient.objects.filter(hook=self.hook)[0]        
        self.assertRecipient(self.hook.recipients.all()[0].chat_id, self.hook.recipients.all()[0].name, recipient=new_recipient)
        
    def test_post_hook_recipient_not_auth(self):
        data = {'chat_id': self.hook.recipients.all()[0].chat_id, 'name': self.hook.recipients.all()[0].name}
        self._test_post_list_not_auth(self._hook_recipient_list_url(), data)
        
    def test_get_recipient_ok(self):
        data = self._test_get_detail_ok(self._hook_recipient_detail_url())
        self.assertRecipient(data['chat_id'], data['name'])
        
    def test_get_recipient_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_recipient_detail_url)
        
    def test_get_recipient_not_auth(self):
        self._test_get_detail_not_auth(self._hook_recipient_detail_url())
        
    def test_get_recipient_not_found(self):
        self._test_get_detail_not_found(self._hook_recipient_detail_url(recipient_pk=12))       
        
    def test_put_recipient_ok(self):
        data = {'chat_id': 9999, 'name': 'new_name'} 
        self._test_put_detail_ok(self._hook_recipient_detail_url(), data, RecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        self.assertEqual(Recipient.objects.get(pk=self.recipient.pk).name, 'new_name')
        self.assertEqual(Recipient.objects.get(pk=self.recipient.pk).chat_id, 9999)
        
    def test_put_recipient_from_other_bot(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_from_other_bot(self._hook_recipient_detail_url, data, RecipientDetail, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_auth(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_not_auth(self._hook_recipient_detail_url(), data, RecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_found(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_not_found(self._hook_recipient_detail_url(recipient_pk=12), data, RecipientDetail, self.bot.pk, self.hook.pk, 12)

    def test_delete_recipient_ok(self):
        self._test_delete_detail_ok(self._hook_recipient_detail_url(), RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_recipient_detail_url, RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_recipient_detail_url(), RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_not_found(self):
        self._test_delete_detail_not_found(self._hook_recipient_detail_url(recipient_pk=12), RecipientDetail, self.bot.pk, self.hook.pk, 12)
