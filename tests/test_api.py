#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, EnvironmentVar, Handler, Hook, Recipient, State, ChatState
from microbot.test import testcases, factories
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from microbot.views import BotDetail, EnvironmentVarDetail, HandlerDetail, HookDetail, RecipientDetail,\
    UrlParameterDetail, HeaderParameterDetail, StateDetail, ChatStateDetail, SourceStateDetail
from django.conf import settings
from django.apps import apps
import json
from microbot.models.handler import HeaderParam, UrlParam
import uuid
import datetime
ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))


class BaseTestAPI(testcases.BaseTestBot):
    
    def setUp(self):
        super(BaseTestAPI, self).setUp()
        self.api = '/microbot/api'
        self.mytoken = '204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc'
        self.mytoken2 = '190880460:AAELDdTxhhfPbtPRyC59qPaVF5VBX4VGVes'
        self.unlikely_id = str(uuid.uuid4())
        
    def assertMicrobotModel(self, id, created_at, updated_at, obj):
        if not id:
            self.assertRegexpMatches(str(obj.id), '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        else:
            self.assertEqual(str(id), str(obj.id))
        if isinstance(created_at, datetime.datetime):
            self.assertEqual(created_at.year, obj.created_at.year)            
        else:
            # just check the year 2016
            self.assertIn(created_at[:3], str(obj.created_at))
        if isinstance(updated_at, datetime.datetime):
            self.assertEqual(updated_at.year, obj.updated_at.year)            
        else:
            self.assertIn(updated_at[:3], str(obj.updated_at))
        
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
    
    def _test_post_list_not_found_required_pre_created(self, url, model, data):
        model.objects.all().delete()
        response = self.client.post(url,
                                    data=json.dumps(data), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
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
    
    def assertBot(self, id, created_at, updated_at, token, enabled, username, first_name, last_name, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(bot.token, token)
        self.assertEqual(bot.enabled, enabled)
        self.assertEqual(bot.user_api.username, username)
        self.assertEqual(bot.user_api.first_name, first_name)
        self.assertEqual(bot.user_api.last_name, last_name)
        self.assertMicrobotModel(id, created_at, updated_at, bot)
        
    def _bot_list_url(self):
        return '%s/bots/' % self.api
        
    def _bot_detail_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/' % (self.api, bot_pk)
    
    def test_get_bots_ok(self):
        data = self._test_get_list_ok(self._bot_list_url())
        self.assertBot(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['token'], data[0]['enabled'], data[0]['info']['username'], 
                       data[0]['info']['first_name'], data[0]['info']['last_name'], None)
        
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
        self.assertBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], data['info']['username'],
                       
                       data['info']['first_name'], data['info']['last_name'])
        
    def test_get_bot_not_auth(self):
        self._test_get_detail_not_auth(self._bot_detail_url())
        
    def test_get_bot_not_found(self):
        self._test_get_detail_not_found(self._bot_detail_url(self.unlikely_id))
        
    def test_put_bot_ok(self):
        self._test_put_detail_ok(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, self.bot.pk)
        self.assertFalse(Bot.objects.get(pk=self.bot.pk).enabled)
        
    def test_put_bot_not_auth(self):
        self._test_put_detail_not_auth(self._bot_detail_url(), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, self.bot.pk)
        
    def test_put_bot_not_found(self):
        self._test_put_detail_not_found(self._bot_detail_url(self.unlikely_id), {'token': self.mytoken, 'enabled': 'False'}, BotDetail, self.unlikely_id)
          
    def test_delete_bot_ok(self):
        self._test_delete_detail_ok(self._bot_detail_url(), BotDetail, self.bot.pk)
        self.assertEqual(Bot.objects.count(), 0)
        
    def test_delete_bot_not_auth(self):
        self._test_delete_detail_not_auth(self._bot_detail_url(), BotDetail, self.bot.pk)
        
    def test_delete_bot_not_found(self):
        self._test_delete_detail_not_found(self._bot_detail_url(self.unlikely_id), BotDetail, self.unlikely_id)       

        
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
    
    def assertEnvVar(self, id, created_at, updated_at, key, value, env_var=None):
        if not env_var:
            env_var = self.env_var
        self.assertEqual(env_var.key, key)
        self.assertEqual(env_var.value, value)
        self.assertMicrobotModel(id, created_at, updated_at, env_var)
        
    def test_get_env_vars_ok(self):
        data = self._test_get_list_ok(self._env_list_url())
        self.assertEnvVar(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value'])
        
    def test_get_env_vars_not_auth(self):
        self._test_get_list_not_auth(self._env_list_url())
        
    def test_post_env_vars_ok(self):
        self._test_post_list_ok(self._env_list_url(), EnvironmentVar, {'key': self.key, 'value': self.value})
        new_env_var = EnvironmentVar.objects.filter(bot=self.bot)[0]
        self.assertEnvVar(None, self.env_var.created_at, self.env_var.updated_at, self.key, self.value, new_env_var)
        
    def test_post_env_vars_not_auth(self):
        self._test_post_list_not_auth(self._env_list_url(), {'key': self.key, 'value': self.value})
                
    def test_get_env_var_ok(self):
        data = self._test_get_detail_ok(self._env_detail_url())
        self.assertEnvVar(data['id'], data['created_at'], data['updated_at'], data['key'], data['value'])
        
    def test_get_env_var_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._env_detail_url)
        
    def test_get_env_var_not_auth(self):
        self._test_get_detail_not_auth(self._env_detail_url())
        
    def test_get_env_var_not_found(self):
        self._test_get_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id))
        
    def test_put_env_var_ok(self):
        self._test_put_detail_ok(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        self.assertEqual(EnvironmentVar.objects.get(pk=self.env_var.pk).value, 'new_value')
        
    def test_put_env_var_from_other_bot(self):
        self._test_put_detail_from_other_bot(self._env_detail_url, {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.env_var.pk)
        
    def test_put_env_var_not_auth(self):
        self._test_put_detail_not_auth(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail,
                                       self.bot.pk, self.env_var.pk)
        
    def test_put_env_var_not_found(self):
        self._test_put_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id), {'key': self.key, 'value': 'new_value'}, 
                                        EnvironmentVarDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_env_var_ok(self):
        self._test_delete_detail_ok(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_env_var_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._env_detail_url, EnvironmentVarDetail, self.env_var.pk)
        
    def test_delete_env_var_not_auth(self):
        self._test_delete_detail_not_auth(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
       
    def test_delete_env_var_not_found(self):
        self._test_delete_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id), EnvironmentVarDetail, self.bot.pk, self.unlikely_id)
        
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
    
    def assertHandler(self, id, created_at, updated_at, name, pattern, response_text_template, response_keyboard_template, enabled, priority, target_state_name, 
                      source_states_names, handler=None):
        if not handler:
            handler = self.handler
        self.assertEqual(handler.name, name)
        self.assertEqual(handler.pattern, pattern)
        self.assertEqual(handler.response.text_template, response_text_template)
        self.assertEqual(handler.response.keyboard_template, response_keyboard_template)
        self.assertEqual(handler.enabled, enabled)
        self.assertEqual(handler.priority, priority)
        self.assertMicrobotModel(id, created_at, updated_at, handler)
        if handler.target_state or target_state_name:
            self.assertEqual(handler.target_state.name, target_state_name)
        if handler.source_states.count() > 0 or source_states_names:
            self.assertEqual(handler.source_states.count(), len(source_states_names))
            for source_state_name in source_states_names:
                handler.source_states.get(name=source_state_name)            
        
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
        self.assertHandler(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                           data[0]['pattern'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                           data[0]['enabled'], data[0]['priority'], None, None)
        
    def test_get_handlers_with_source_states_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.source_states.add(self.state)
        data = self._test_get_list_ok(self._handler_list_url())
        self.assertHandler(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                           data[0]['pattern'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                           data[0]['enabled'], data[0]['priority'], None, [self.state.name])
        
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
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, None, None, new_handler)
        
    def test_post_handlers_with_target_state_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'target_state': {'name': self.state.name}, 'priority': self.handler.priority,
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
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, self.handler.target_state.name, None, new_handler)
        self.assertEqual(self.handler.target_state, new_handler.target_state)
        
    def test_post_handlers_with_target_state_new_state_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'target_state': {'name': 'new_state'}, 'priority': self.handler.priority,
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
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, new_handler.target_state.name, None, new_handler)
        
    def test_post_handlers_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': self.handler.request}
        self._test_post_list_not_auth(self._handler_list_url(), data)
        
    def test_get_handler_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = self._test_get_detail_ok(self._handler_detail_url())
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], data['pattern'], 
                           data['response']['text_template'], data['response']['keyboard_template'], 
                           data['enabled'], data['priority'], data['target_state']['name'], None)
        
    def test_get_handler_with_source_states_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.source_states.add(self.state)
        data = self._test_get_detail_ok(self._handler_detail_url())
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], data['pattern'], 
                           data['response']['text_template'], data['response']['keyboard_template'], 
                           data['enabled'], data['priority'], None, [data['source_states'][0]['name']])

    def test_get_handler_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_detail_url)
        
    def test_get_handler_not_auth(self):
        self._test_get_detail_not_auth(self._handler_detail_url())
        
    def test_get_handler_not_found(self):
        self._test_get_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id))
        
    def test_put_handler_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
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
        
    def test_put_handler_with_target_new_state_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,                                                                                 
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            },
                'target_state': {'name': 'new_state'}, 
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).target_state.name, 'new_state')
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_with_target_state_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,                                                                                 
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': 2,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            },
                'target_state': {'name': self.state.name}, 
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).priority, 2)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).target_state, self.state)
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_from_other_bot(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_from_other_bot(self._handler_detail_url, data, HandlerDetail, self.handler.pk)
        
    def test_put_handler_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_auth(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_put_handler_not_found(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id), data, HandlerDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_handler_ok(self):
        self._test_delete_detail_ok(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_handler_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_detail_url, HandlerDetail, self.handler.pk)
        
    def test_delete_handler_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_delete_handler_not_found(self):
        self._test_delete_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id), HandlerDetail, self.bot.pk, self.unlikely_id)

        
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
        
    def assertUrlParam(self, id, created_at, updated_at, key, value_template, url_param=None):
        if not url_param:
            url_param = self.url_param
        self.assertEqual(url_param.key, key)
        self.assertEqual(url_param.value_template, value_template)
        self.assertMicrobotModel(id, created_at, updated_at, url_param)

    def assertHeaderParam(self, id, created_at, updated_at, key, value_template, header_param=None):
        if not header_param:
            header_param = self.header_param
        self.assertEqual(header_param.key, key)
        self.assertEqual(header_param.value_template, value_template)
        self.assertMicrobotModel(id, created_at, updated_at, header_param)
        
    def test_get_handler_url_params_ok(self):
        data = self._test_get_list_ok(self._handler_url_param_list_url())
        self.assertUrlParam(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_url_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_url_param_list_url())
        
    def test_post_handler_url_params_ok(self):
        data = {'key': self.handler.request.url_parameters.all()[0].key,
                'value_template': self.handler.request.url_parameters.all()[0].value_template}                         
        self._test_post_list_ok(self._handler_url_param_list_url(), UrlParam, data)
        new_url_param = UrlParam.objects.filter(request=self.handler.request)[0]
        self.assertUrlParam(None, self.url_param.created_at, self.url_param.updated_at, self.url_param.key, self.url_param.value_template, new_url_param)
        
    def test_post_handler_url_params_not_auth(self):
        data = {'key': self.url_param.key,
                'value_template': self.url_param.value_template}
        self._test_post_list_not_auth(self._handler_url_param_list_url(), data)
            
    def test_get_handler_url_param_ok(self):
        data = self._test_get_detail_ok(self._handler_url_param_detail_url())
        self.assertUrlParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'])
        
    def test_get_handler_url_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_url_param_detail_url)
        
    def test_get_handler_url_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_url_param_detail_url())
        
    def test_get_handler_url_param_not_found(self):
        self._test_get_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id))
        
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
        self._test_put_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id), data, 
                                        UrlParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_url_param_ok(self):
        self._test_delete_detail_ok(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        self.assertEqual(UrlParam.objects.count(), 0)
        
    def test_delete_handler_url_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_url_param_detail_url, UrlParameterDetail, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id), 
                                           UrlParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
        
    def test_get_handler_header_params_ok(self):
        data = self._test_get_list_ok(self._handler_header_param_list_url())
        self.assertHeaderParam(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_header_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_header_param_list_url())
        
    def test_post_handler_header_params_ok(self):
        data = {'key': self.handler.request.header_parameters.all()[0].key,
                'value_template': self.handler.request.header_parameters.all()[0].value_template}                         
        self._test_post_list_ok(self._handler_header_param_list_url(), HeaderParam, data)
        new_header_param = HeaderParam.objects.filter(request=self.handler.request)[0]
        self.assertHeaderParam(None, self.header_param.created_at, self.header_param.updated_at, self.header_param.key, 
                               self.header_param.value_template, new_header_param)
        
    def test_post_handler_header_params_not_auth(self):
        data = {'key': self.header_param.key,
                'value_template': self.header_param.value_template}
        self._test_post_list_not_auth(self._handler_header_param_list_url(), data)
        
    def test_get_handler_header_param_ok(self):
        data = self._test_get_detail_ok(self._handler_header_param_detail_url())
        self.assertHeaderParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'])
        
    def test_get_handler_header_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_header_param_detail_url)
        
    def test_get_handler_header_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_header_param_detail_url())
        
    def test_get_handler_header_param_not_found(self):
        self._test_get_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id))
        
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
        self._test_put_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id), data, 
                                        HeaderParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_header_param_ok(self):
        self._test_delete_detail_ok(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        self.assertEqual(HeaderParam.objects.count(), 0)
        
    def test_delete_handler_header_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_header_param_detail_url, HeaderParameterDetail, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id), 
                                           HeaderParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
    
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

    def assertHook(self, id, created_at, updated_at, name, response_text_template, response_keyboard_template, enabled, recipients, hook=None):
        if not hook:
            hook = self.hook
        self.assertEqual(hook.name, name)
        self.assertEqual(hook.response.text_template, response_text_template)
        self.assertEqual(hook.response.keyboard_template, response_keyboard_template)
        self.assertEqual(hook.enabled, enabled)
        self.assertMicrobotModel(id, created_at, updated_at, hook)
        self.assertEqual(hook.recipients.count(), len(recipients))
        # check recipients
        for recipient in recipients:
            self.assertEqual(Recipient.objects.get(chat_id=recipient['chat_id']).chat_id, recipient['chat_id'])
            self.assertEqual(Recipient.objects.get(chat_id=recipient['chat_id']).name, recipient['name'])
        
    def test_get_hooks_ok(self):
        data = self._test_get_list_ok(self._hook_list_url())
        self.assertHook(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                        data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
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
        self.assertHook(None, self.hook.created_at, self.hook.updated_at, self.hook.name, self.hook.response.text_template, 
                        self.hook.response.keyboard_template,
                        False, recipients, hook=new_hook)
        
    def test_post_hooks_not_auth(self):
        data = {'name': self.hook.name, 'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.recipients.all()]}
        self._test_post_list_not_auth(self._hook_list_url(), data)
        
    def test_get_hook_ok(self):
        data = self._test_get_detail_ok(self._hook_detail_url())
        self.assertHook(data['id'], data['created_at'], data['updated_at'], data['name'], 
                        data['response']['text_template'], data['response']['keyboard_template'], data['enabled'],
                        data['recipients'])
        
    def test_get_hook_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_detail_url)
        
    def test_get_hook_not_auth(self):
        self._test_get_detail_not_auth(self._hook_detail_url())
        
    def test_get_hook_not_found(self):
        self._test_get_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id))
        
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
        self._test_put_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id), data, HookDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_hook_ok(self):
        self._test_delete_detail_ok(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_detail_url, HookDetail, self.hook.pk)
        
    def test_delete_hook_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_not_found(self):
        self._test_delete_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id), HookDetail, self.bot.pk, self.unlikely_id)


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
        self._test_get_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id))       
        
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
        self._test_put_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), data, 
                                        RecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)

    def test_delete_recipient_ok(self):
        self._test_delete_detail_ok(self._hook_recipient_detail_url(), RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_recipient_detail_url, RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_recipient_detail_url(), RecipientDetail, self.bot.pk, self.hook.pk, self.hook.recipients.all()[0].pk)
        
    def test_delete_recipient_not_found(self):
        self._test_delete_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), 
                                           RecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)

class TestStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        
    def _state_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/states/' % (self.api, bot_pk)
    
    def _state_detail_url(self, bot_pk=None, state_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not state_pk:
            state_pk = self.state.pk
        return '%s/bots/%s/states/%s/' % (self.api, bot_pk, state_pk)
    
    def assertState(self, id, created_at, updated_at, name, state=None):
        if not state:
            state = self.state
        self.assertEqual(state.name, name)
        self.assertMicrobotModel(id, created_at, updated_at, state)
        
    def test_get_states_ok(self):
        data = self._test_get_list_ok(self._state_list_url())
        self.assertState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'])
        
    def test_get_states_not_auth(self):
        self._test_get_list_not_auth(self._state_list_url())
        
    def test_post_states_ok(self):
        self._test_post_list_ok(self._state_list_url(), State, {'name': self.state.name})
        new_state = State.objects.filter(bot=self.bot)[0]
        self.assertState(None, self.state.created_at, self.state.updated_at, self.state.name, new_state)
        
    def test_post_states_not_auth(self):
        self._test_post_list_not_auth(self._state_list_url(), {'name': self.state.name})
                
    def test_get_state_ok(self):
        data = self._test_get_detail_ok(self._state_detail_url())
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'])
        
    def test_get_state_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._state_detail_url)
        
    def test_get_state_not_auth(self):
        self._test_get_detail_not_auth(self._state_detail_url())
        
    def test_get_state_var_not_found(self):
        self._test_get_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id))
        
    def test_put_state_ok(self):
        self._test_put_detail_ok(self._state_detail_url(), {'name': 'new_value'}, StateDetail, self.bot.pk, self.state.pk)
        self.assertEqual(State.objects.get(pk=self.state.pk).name, 'new_value')
        
    def test_put_state_from_other_bot(self):
        self._test_put_detail_from_other_bot(self._state_detail_url, {'name': 'new_value'}, StateDetail, self.state.pk)
        
    def test_put_state_not_auth(self):
        self._test_put_detail_not_auth(self._state_detail_url(), {'name': 'new_value'}, StateDetail,
                                       self.bot.pk, self.state.pk)
        
    def test_put_state_not_found(self):
        self._test_put_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id), {'name': 'new_value'}, StateDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_state_ok(self):
        self._test_delete_detail_ok(self._state_detail_url(), StateDetail, self.bot.pk, self.state.pk)
        self.assertEqual(State.objects.count(), 0)
        
    def test_delete_state_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._state_detail_url, StateDetail, self.state.pk)
        
    def test_delete_state_not_auth(self):
        self._test_delete_detail_not_auth(self._state_detail_url(), StateDetail, self.bot.pk, self.state.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)
        
        
class TestChatStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestChatStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        self.chat = factories.ChatAPIFactory(id=self.update.message.chat.id,
                                             type=self.update.message.chat.type, 
                                             title=self.update.message.chat.title,
                                             username=self.update.message.chat.username,
                                             first_name=self.update.message.chat.first_name,
                                             last_name=self.update.message.chat.last_name)
        self.chatstate = factories.ChatStateFactory(state=self.state,
                                                    chat=self.chat)
        
    def _chatstate_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/chatstates/' % (self.api, bot_pk)
    
    def _chatstate_detail_url(self, bot_pk=None, chatstate_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not chatstate_pk:
            chatstate_pk = self.chatstate.pk
        return '%s/bots/%s/chatstates/%s/' % (self.api, bot_pk, chatstate_pk)
    
    def assertChatState(self, id, created_at, updated_at, name, chat_id, chatstate=None):
        if not chatstate:
            chatstate = self.chatstate
        self.assertEqual(chatstate.state.name, name)
        self.assertEqual(chatstate.chat.id, chat_id)
        self.assertMicrobotModel(id, created_at, updated_at, chatstate)
        
    def test_get_chatstates_ok(self):
        data = self._test_get_list_ok(self._chatstate_list_url())
        self.assertChatState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['state']['name'], data[0]['chat'])
        
    def test_get_chatstates_not_auth(self):
        self._test_get_list_not_auth(self._chatstate_list_url())
        
    def test_post_chatstates_ok(self):
        self._test_post_list_ok(self._chatstate_list_url(), ChatState, {'chat': self.chat.id, 'state': {'name': self.state.name}})
        new_chatstate = ChatState.objects.filter(state=self.state)[0]
        self.assertChatState(None, self.chatstate.created_at, self.chatstate.updated_at, self.chatstate.state.name, self.chatstate.chat.id, new_chatstate)
        
    def test_post_chatstates_new_state_not_found(self):
        self._test_post_list_not_found_required_pre_created(self._chatstate_list_url(), ChatState, {'chat': self.chat.id, 'state': {'name': 'joolo'}})
        
    def test_post_chatstates_not_auth(self):
        self._test_post_list_not_auth(self._chatstate_list_url(), {'chat': self.chat.id, 'state': {'name': self.state.name}})
                
    def test_get_chatstate_ok(self):
        data = self._test_get_detail_ok(self._chatstate_detail_url())
        self.assertChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'])
        
    def test_get_chatstate_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._chatstate_detail_url)
        
    def test_get_chatstate_not_auth(self):
        self._test_get_detail_not_auth(self._chatstate_detail_url())
        
    def test_get_chatstate_var_not_found(self):
        self._test_get_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id))
        
    def test_put_chatstate_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'chat': self.chat.id, 'state': {'name': new_state.name}}, 
                                 ChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(ChatState.objects.get(pk=self.chatstate.pk).state.name, new_state.name)
        
    def test_put_chatstate_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_from_other_bot(self._chatstate_detail_url, 
                                             {'chat': self.chat.id, 'state': {'name': new_state.name}}, 
                                             ChatStateDetail, self.chatstate.pk)
        
    def test_put_chatstate_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_auth(self._chatstate_detail_url(), {'chat': self.chat.id, 'state': {'name': new_state.name}}, ChatStateDetail,
                                       self.bot.pk, self.chatstate.pk)
        
    def test_put_chatstate_not_found(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), 
                                        {'chat': self.chat.id, 'state': {'name': new_state.name}}, ChatStateDetail, 
                                        self.bot.pk, self.unlikely_id)
          
    def test_delete_chatstate_ok(self):
        self._test_delete_detail_ok(self._chatstate_detail_url(), ChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(ChatState.objects.count(), 0)
        
    def test_delete_chatstate_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._chatstate_detail_url, ChatStateDetail, self.chatstate.pk)
        
    def test_delete_chatstate_not_auth(self):
        self._test_delete_detail_not_auth(self._chatstate_detail_url(), ChatStateDetail, self.bot.pk, self.chatstate.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)
        
class TestHandlerSourceStatesAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerSourceStatesAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.handler.source_states.add(self.state)
    
    def _handler_source_state_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/sourcestates/' % (self.api, bot_pk, handler_pk)
    
    def _handler_source_state_detail_url(self, bot_pk=None, handler_pk=None, source_state_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not source_state_pk:
            source_state_pk = self.state.pk
        return '%s/bots/%s/handlers/%s/sourcestates/%s/' % (self.api, bot_pk, handler_pk, source_state_pk)             
        
    def assertSourceStates(self, names, source_states=None):
        if not source_states:
            source_states = self.handler.source_states
        self.assertEqual(source_states.count(), len(names))
        for name in names:
            source_states.get(name=name)
    
    def assertState(self, id, created_at, updated_at, name, state=None):
        if not state:
            state = self.state
        self.assertEqual(state.name, name)
        self.assertMicrobotModel(id, created_at, updated_at, state)
    
    def test_get_handler_source_states_ok(self):
        data = self._test_get_list_ok(self._handler_source_state_list_url())
        self.assertState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'])

    def test_get_handler_source_states_not_auth(self):
        self._test_get_list_not_auth(self._handler_source_state_list_url())
        
    def test_post_handler_source_states_ok(self):
        data = {'name': self.state.name}                         
        self._test_post_list_ok(self._handler_source_state_list_url(), State, data)
        new_source_states = Handler.objects.get(pk=self.handler.pk).source_states
        self.assertSourceStates([obj.name for obj in self.handler.source_states.all()], new_source_states)
        
    def test_post_handler_source_states_not_auth(self):
        data = {'name': self.state.name}
        self._test_post_list_not_auth(self._handler_source_state_list_url(), data)
            
    def test_get_handler_source_state_ok(self):
        data = self._test_get_detail_ok(self._handler_source_state_detail_url())
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'])
        
    def test_get_handler_source_state_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_source_state_detail_url)
        
    def test_get_handler_source_state_not_auth(self):
        self._test_get_detail_not_auth(self._handler_source_state_detail_url())
        
    def test_get_handler_source_state_not_found(self):
        self._test_get_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id))
        
    def test_put_handler_source_state_ok(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}
        self._test_put_detail_ok(self._handler_source_state_detail_url(), data, SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        self.assertEqual(self.handler.source_states.count(), 1)
        self.assertEqual(self.handler.source_states.all()[0].name, 'new_state')
                
    def test_put_handler_source_state_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}
        self._test_put_detail_from_other_bot(self._handler_source_state_detail_url, data, SourceStateDetail, self.handler.pk, self.state.pk)
        
    def test_put_handler_source_state_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}        
        self._test_put_detail_not_auth(self._handler_source_state_detail_url(), data, SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        
    def test_put_handler_source_state_not_found(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}  
        self._test_put_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id), data, 
                                        SourceStateDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_source_state_ok(self):
        self._test_delete_detail_ok(self._handler_source_state_detail_url(), SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        self.assertEqual(UrlParam.objects.count(), 0)
        
    def test_delete_handler_source_state_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_source_state_detail_url, SourceStateDetail, self.handler.pk, self.state.pk)
        
    def test_delete_handler_source_state_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_source_state_detail_url(), SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        
    def test_delete_handler_source_state_not_found(self):
        self._test_delete_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id), 
                                           SourceStateDetail, self.bot.pk, self.handler.pk, self.unlikely_id)