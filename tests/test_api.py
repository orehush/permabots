#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, EnvironmentVar
from microbot.test import testcases
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from microbot.views import BotDetail, EnvironmentVarDetail
from django.conf import settings
from django.apps import apps

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
        
    def test_delete_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url())
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self._env_detail_url(env_pk=12))
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 