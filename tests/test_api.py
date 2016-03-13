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
    
    def test_get_bots_ok(self):
        response = self.client.get(self.api + '/bots/', HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(self.bot.token, data[0]['token'])
        self.assertEqual(self.bot.enabled, data[0]['enabled'])
        self.assertEqual(self.bot.user_api.username, data[0]['info']['username'])
        self.assertEqual(self.bot.user_api.first_name, data[0]['info']['first_name'])
        self.assertEqual(self.bot.user_api.last_name, data[0]['info']['last_name'])
        
    def test_get_bots_not_auth(self):
        response = self.client.get(self.api + '/bots/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_bots_ok(self):
        Bot.objects.all().delete()
        response = self.client.post(self.api + '/bots/', 
                                    data={'token': self.mytoken, 'enabled': 'True'}, 
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_bot = Bot.objects.get(token=self.mytoken)
        self.assertEqual(new_bot.token, self.mytoken)
        self.assertTrue(new_bot.enabled)
        
    def test_post_bots_not_auth(self):
        response = self.client.post(self.api + '/bots/', 
                                    data={'token': self.mytoken, 'enabled': 'True'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_bot_ok(self):
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(self.bot.token, data['token'])
        self.assertEqual(self.bot.enabled, data['enabled'])
        self.assertEqual(self.bot.user_api.username, data['info']['username'])
        self.assertEqual(self.bot.user_api.first_name, data['info']['first_name'])
        self.assertEqual(self.bot.user_api.last_name, data['info']['last_name'])
        
    def test_get_bot_not_auth(self):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/',
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_bot_not_found(self):
        response = self.client.get(self.api + '/bots/12/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_bot_ok(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(self.bot.pk) + '/', {'token': self.mytoken, 'enabled': 'False'})
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Bot.objects.get(pk=self.bot.pk).enabled)
        
    def test_put_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(self.bot.pk) + '/', {'token': self.mytoken, 'enabled': 'False'})
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/12/', {'token': self.mytoken, 'enabled': 'False'})
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
          
    def test_delete_bot_ok(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/')
        force_authenticate(request, user=self.bot.owner)
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bot.objects.count(), 0)
        
    def test_delete_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/')
        response = BotDetail.as_view()(request, self.bot.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/12/')
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
        
    def test_get_env_vars_ok(self):
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/env/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(self.env_var.key, data[0]['key'])
        self.assertEqual(self.env_var.value, data[0]['value'])
        
    def test_get_env_vars_not_auth(self):
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/env/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_env_vars_ok(self):
        EnvironmentVar.objects.all().delete()
        response = self.client.post(self.api + '/bots/' + str(self.bot.pk) + '/env/', 
                                    data={'key': self.key, 'value': self.value}, 
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_env_var = EnvironmentVar.objects.filter(bot=self.bot)[0]
        self.assertEqual(new_env_var.key, self.key)
        self.assertTrue(new_env_var.value, self.value)
        
    def test_post_env_vars_not_auth(self):
        response = self.client.post(self.api + '/bots/' + str(self.bot.pk) + '/env/', 
                                    data={'key': self.key, 'value': self.value})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                
    def test_get_env_var_ok(self):
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(self.env_var.key, data['key'])
        self.assertEqual(self.env_var.value, data['value'])
        
    def test_get_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        response = self.client.get(self.api + '/bots/' + str(new_bot.pk) + '/env/' + str(self.env_var.pk) + '/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_env_var_not_auth(self):
        new_user = ModelUser.objects.create_user(username='username',
                                                 email='username@test.com',
                                                 password='password')
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/',
                                   HTTP_AUTHORIZATION=self._gen_token(new_user.auth_token))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_env_var_not_found(self):
        response = self.client.get(self.api + '/bots/' + str(self.bot.pk) + '/env/12/',
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_env_var_ok(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/', 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EnvironmentVar.objects.get(pk=self.env_var.pk).value, 'new_value')
        
    def test_put_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(new_bot.pk) + '/env/' + str(self.env_var.pk) + '/', 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, new_bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_put_env_var_not_auth(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/', 
                              {'key': self.key, 'value': 'new_value'})
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_env_var_not_found(self):
        factory = APIRequestFactory()
        request = factory.put(self.api + '/bots/' + str(self.bot.pk) + '/env/12/', 
                              {'key': self.key, 'value': 'new_value'})
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
          
    def test_delete_env_var_ok(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/')
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_env_var_from_other_bot(self):
        new_bot = Bot.objects.create(owner=self.bot.owner,
                                     token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/')
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, new_bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_bot_not_auth(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/env/' + str(self.env_var.pk) + '/')
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, self.env_var.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_bot_not_found(self):
        factory = APIRequestFactory()
        request = factory.delete(self.api + '/bots/' + str(self.bot.pk) + '/env/12/')
        force_authenticate(request, user=self.bot.owner)
        response = EnvironmentVarDetail.as_view()(request, self.bot.pk, 12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 