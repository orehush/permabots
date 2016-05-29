# -*- coding: utf-8 -*-
from permabots.models import Bot, TelegramBot
from permabots.test import testcases
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.conf import settings
from django.apps import apps
import json
import uuid
import datetime
try:
    from unittest import mock
except ImportError:
    import mock  # noqa
ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))


class BaseTestAPI(testcases.BaseTestBot):
    
    def setUp(self):
        super(BaseTestAPI, self).setUp()
        self.api = '/permabots/api'
        self.mytoken = '204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc'
        self.mytoken2 = '190880460:AAELDdTxhhfPbtPRyC59qPaVF5VBX4VGVes'
        self.unlikely_id = str(uuid.uuid4())
        self.my_api_key = '605c50e6-9ef7-4e71-8538-d72e2489a7b5'
        self.my_username = 'permatest' 
        self.my_messenger_token = 'EAAO4bzdZBWZAABAO7TNopLq0v29dhCvoZAnZBaImXkBDiS23sblQb6nhThn4TByZBifvpuJGXZChXWt3wP2PcCXeVrXJHlcgMlNsurEgAIz419d4KkoCuvEeaLlwwkZBFpoirIBwNsgJZCtaiaH9dPC4m0Tit1wKN2CEAxAfR0V9eQZDZD'  # noqa
        
    def create_bot(self, owner, token):
        with mock.patch("telegram.bot.Bot.set_webhook", callable=mock.MagicMock()):
            bot = Bot.objects.create(name="new_bot",
                                     owner=owner)
            telegram_bot = TelegramBot.objects.create(token=token)
            bot.telegram_bot = telegram_bot
            bot.save()
            return telegram_bot
                     
    def assertPermabotsModel(self, id, created_at, updated_at, obj):
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
    
    def _test_post_list_validation_error(self, url, model, data):
        model.objects.all().delete()
        response = self.client.post(url,
                                    data=json.dumps(data), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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
        return response.data

    def _test_put_detail_validation_error(self, url, data, view, *args):
        factory = APIRequestFactory()
        request = factory.put(url, data, format="json")
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, *args)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        return response

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
        
        new_bot = self.create_bot(owner=self.bot.owner,
                                  token=self.mytoken2)
        response = self.client.get(func_url(new_bot.pk, *args),
                                   HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_put_detail_from_other_bot(self, func_url, data, view, *args):
        new_bot = self.create_bot(owner=self.bot.owner,
                                  token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.put(func_url(new_bot.pk), data, format="json")
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, new_bot.pk, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def _test_delete_detail_from_other_bot(self, func_url, view, *args):
        new_bot = self.create_bot(owner=self.bot.owner,
                                  token=self.mytoken2)
        factory = APIRequestFactory()
        request = factory.delete(func_url(new_bot.pk))
        force_authenticate(request, user=self.bot.owner)
        response = view.as_view()(request, new_bot.pk, *args)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)