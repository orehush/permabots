#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, EnvironmentVar, Handler
from microbot.test import testcases, factories
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from microbot.views import BotDetail, EnvironmentVarDetail, HandlerDetail
from django.conf import settings
from django.apps import apps
import json
from microbot.models.handler import HeaderParam, UrlParam
ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))

class BaseTestAPI(testcases.BaseTestBot):

    def _gen_token(self, token):
        return 'Token  %s' % str(token)
    
    def setUp(self):
        super(BaseTestAPI, self).setUp()
        self.api = '/microapi'
        self.mytoken = '204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc'
        self.mytoken2 = '190880460:AAELDdTxhhfPbtPRyC59qPaVF5VBX4VGVes'
        
class TestBotAPI(BaseTestAPI):
    
    def assertBot(self, token, enabled, username, first_name, last_name, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(bot.token,token)
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
        response = self.client.get(self._bot_list_url(), HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertBot(data[0]['token'], data[0]['enabled'], data[0]['info']['username'], 
                       data[0]['info']['first_name'], data[0]['info']['last_name'])
        
    def test_get_bots_not_auth(self):
        response = self.client.get(self._bot_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_bots_ok(self):
        Bot.objects.all().delete()
        response = self.client.post(self._bot_list_url(),
                                    data={'token': self.mytoken, 'enabled': 'True'}, 
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_bot = Bot.objects.get(token=self.mytoken)
        self.assertEqual(new_bot.token, self.mytoken)
        self.assertTrue(new_bot.enabled)
        
    def test_post_bots_not_auth(self):
        response = self.client.post(self._bot_list_url(), 
                                    data={'token': self.mytoken, 'enabled': 'True'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_bot_ok(self):
        response = self.client.get(self._bot_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertBot(data['token'], data['enabled'], data['info']['username'],
                       data['info']['first_name'], data['info']['last_name'])
        
    def test_get_bot_not_auth(self):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(self._bot_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_bot_not_found(self):
        response = self.client.get(self._bot_detail_url(12),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_bot_ok(self):
        factory = APIRequestFactory()
        request = factory.put(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'})
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Bot.objects.get(pk=self.bot.pk).enabled)
        
    def test_put_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.put(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'})
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.put(self._bot_detail_url(12), {'token': self.mytoken, 'enabled': 'False'})
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
          
    def test_delete_bot_ok(self):
        factory = APIRequestFactory()
        request = factory.delete(self._bot_detail_url())
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bot.objects.count(), 0)
        
    def test_delete_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self._bot_detail_url())
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self._bot_detail_url(12))
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
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
        response = self.client.get(self._env_list_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEnvVar(data[0]['key'], data[0]['value'])
        
    def test_get_env_vars_not_auth(self):
        response = self.client.get(self._env_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_env_vars_ok(self):
        EnvironmentVar.objects.all().delete()
        response = self.client.post(self._env_list_url(), 
                                    data={'key': self.key, 'value': self.value}, 
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_env_var = EnvironmentVar.objects.filter(bot=self.bot)[0]
        self.assertEnvVar(self.key, self.value, new_env_var)
        
    def test_post_env_vars_not_auth(self):
        response = self.client.post(self._env_list_url(), 
                                    data={'key': self.key, 'value': self.value})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                
    def test_get_env_var_ok(self):
        response = self.client.get(self._env_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEnvVar(data['key'], data['value'])
        
    def test_get_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        response = self.client.get(self._env_detail_url(new_bot.pk),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_env_var_not_auth(self):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(self._env_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_env_var_not_found(self):
        response = self.client.get(self._env_detail_url(env_pk=12),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_env_var_ok(self):
        factory = APIRequestFactory()
        request = factory.put(self._env_detail_url(), 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EnvironmentVar.objects.get(pk=self.env_var.pk).value, 'new_value')
        
    def test_put_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.put(self._env_detail_url(new_bot.pk), 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, new_bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_env_var_not_auth(self):
        factory = APIRequestFactory()
        request = factory.put(self._env_detail_url(), 
                              {'key': self.key, 'value': 'new_value'})
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_env_var_not_found(self):
        factory = APIRequestFactory()
        request = factory.put(self._env_detail_url(env_pk=12), 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
          
    def test_delete_env_var_ok(self):
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url())
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url(new_bot.pk))
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, new_bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_env_var_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url())
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_env_var_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url(env_pk=12))
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
        
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
    
    def assertHandler(self, pattern, response_text_template, response_keyboard_template, enabled, handler=None):
        if not handler:
            handler = self.handler
        self.assertEqual(handler.pattern, pattern)
        self.assertEqual(handler.response_text_template, response_text_template)
        self.assertEqual(handler.response_keyboard_template, response_keyboard_template)
        self.assertEqual(handler.enabled, enabled)
        
    def test_get_handlers_ok(self):
        response = self.client.get(self._handler_list_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertHandler(data[0]['pattern'], data[0]['response_text_template'], data[0]['response_keyboard_template'],
                           data[0]['enabled'])
        
    def test_get_handlers_not_auth(self):
        response = self.client.get(self._handler_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_handlers_ok(self):
        Handler.objects.all().delete()
        data = {'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                                          'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                                          'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                                      'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                         'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                                      'header_parameters' : [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                              'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                                      }                                                                         
                                          }
        response = self.client.post(self._handler_list_url(), 
                                    data=json.dumps(data), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(self.handler.pattern, self.handler.response_text_template, self.handler.response_keyboard_template,
                          False, new_handler)
        
    def test_post_handlers_not_auth(self):
        response = self.client.post(self._handler_list_url(), 
                                    data={'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                                          'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                                          'request': self.handler.request})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
    def test_get_handler_ok(self):
        response = self.client.get(self._handler_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertHandler(data['pattern'], data['response_text_template'], data['response_keyboard_template'], data['enabled'])
        
    def test_get_handler_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        response = self.client.get(self._handler_detail_url(new_bot.pk),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_handler_not_auth(self):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(self._handler_detail_url(),
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_handler_not_found(self):
        response = self.client.get(self._handler_detail_url(handler_pk=12),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_handler_ok(self):
        factory = APIRequestFactory()
        request = factory.put(self._handler_detail_url(), 
                              {'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                               'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                               'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                           'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                               'value_template': 'new_url_param_value'}],
                                           'header_parameters' : [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                   'value_template': 'new_header_param_value'}]}},
                              format='json')
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, self.bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.put(self._handler_detail_url(new_bot.pk), 
                              {'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                               'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                               'request': self.handler.request})
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, new_bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_handler_not_auth(self):
        factory = APIRequestFactory()
        request = factory.put(self._handler_detail_url(), 
                              {'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                               'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                               'request': self.handler.request})
        response = HandlerDetail.as_view()(request, self.bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_handler_not_found(self):
        factory = APIRequestFactory()
        request = factory.put(self._handler_detail_url(handler_pk=12), 
                              {'pattern': self.handler.pattern, 'response_text_template': self.handler.response_text_template,
                               'response_keyboard_template': self.handler.response_keyboard_template, 'enabled': False,
                               'request': self.handler.request})
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
          
    def test_delete_handler_ok(self):
        factory = APIRequestFactory()
        request = factory.delete(self._handler_detail_url())
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, self.bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_handler_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.delete(self._handler_detail_url(new_bot.pk))
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, new_bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_handler_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self._handler_detail_url())
        response = HandlerDetail.as_view()(request, self.bot.pk, self.handler.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_handler_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self._handler_detail_url(handler_pk=12))
        force_authenticate(request, user=self.bot.owner)
        response = HandlerDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
        
    