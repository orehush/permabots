#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, TelegramBot, KikBot
from rest_framework import status
from microbot.views import BotDetail, TelegramBotDetail, KikBotDetail
import json
from tests.api.base import BaseTestAPI

class TestBotAPI(BaseTestAPI):
    
    def assertBot(self, id, created_at, updated_at, name, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(bot.name, name)
        self.assertMicrobotModel(id, created_at, updated_at, bot)
        
    def _bot_list_url(self):
        return '%s/bots/' % self.api
        
    def _bot_detail_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/' % (self.api, bot_pk)
    
    def test_get_bots_ok(self):
        data = self._test_get_list_ok(self._bot_list_url())
        self.assertBot(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], None)
        
    def test_get_bots_not_auth(self):
        self._test_get_list_not_auth(self._bot_list_url())
        
    def test_post_bots_ok(self):
        data = self._test_post_list_ok(self._bot_list_url(), Bot, {'name': 'new_name'})
        new_bot = Bot.objects.all()[0]
        self.assertEqual(new_bot.name, 'new_name')
        self.assertBot(data['id'], data['created_at'], data['updated_at'], data['name'], new_bot)
        
    def test_post_bots_not_auth(self):
        self._test_post_list_not_auth(self._bot_list_url(), {'name': 'new_name'})
        
    def test_get_bot_ok(self):
        data = self._test_get_detail_ok(self._bot_detail_url())
        self.assertBot(data['id'], data['created_at'], data['updated_at'], data['name'])
        
    def test_get_bot_not_auth(self):
        self._test_get_detail_not_auth(self._bot_detail_url())
        
    def test_get_bot_not_found(self):
        self._test_get_detail_not_found(self._bot_detail_url(self.unlikely_id))
        
    def test_put_bot_ok(self):
        data = self._test_put_detail_ok(self._bot_detail_url(), {'name': 'new_name'}, BotDetail, self.bot.pk)
        updated = Bot.objects.get(pk=self.bot.pk)
        self.assertEqual(updated.name, 'new_name')
        self.assertBot(data['id'], data['created_at'], data['updated_at'], data['name'], updated)

    def test_put_bot_not_auth(self):
        self._test_put_detail_not_auth(self._bot_detail_url(), {'name': 'new_name'}, BotDetail, self.bot.pk)
        
    def test_put_bot_not_found(self):
        self._test_put_detail_not_found(self._bot_detail_url(self.unlikely_id), {'name': 'new_name'}, BotDetail, self.unlikely_id)
          
    def test_delete_bot_ok(self):
        self._test_delete_detail_ok(self._bot_detail_url(), BotDetail, self.bot.pk)
        self.assertEqual(Bot.objects.count(), 0)
        
    def test_delete_bot_not_auth(self):
        self._test_delete_detail_not_auth(self._bot_detail_url(), BotDetail, self.bot.pk)
        
    def test_delete_bot_not_found(self):
        self._test_delete_detail_not_found(self._bot_detail_url(self.unlikely_id), BotDetail, self.unlikely_id)
        
        
class TestTelegramBotAPI(BaseTestAPI):
    
    def assertTelegramBot(self, id, created_at, updated_at, token, enabled, username, first_name, last_name, telegram_bot=None):
        if not telegram_bot:
            telegram_bot = self.bot.telegram_bot
        self.assertEqual(telegram_bot.token, token)
        self.assertEqual(telegram_bot.enabled, enabled)
        self.assertEqual(telegram_bot.user_api.username, username)
        self.assertEqual(telegram_bot.user_api.first_name, first_name)
        self.assertEqual(telegram_bot.user_api.last_name, last_name)
        self.assertMicrobotModel(id, created_at, updated_at, telegram_bot)
        
    def _telegram_bot_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/telegram/' % (self.api, bot_pk)
        
    def _telegram_bot_detail_url(self, bot_pk=None, telegram_bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not telegram_bot_pk:
            telegram_bot_pk = self.bot.telegram_bot.pk
        return '%s/bots/%s/telegram/%s/' % (self.api, bot_pk, telegram_bot_pk)
    
    def test_get_telegram_bots_ok(self):
        data = self._test_get_list_ok(self._telegram_bot_list_url())
        self.assertTelegramBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], data['info']['username'], 
                               data['info']['first_name'], data['info']['last_name'], None)
        
    def test_get_telegram_bots_not_auth(self):
        self._test_get_list_not_auth(self._telegram_bot_list_url())
        
    def test_telegram_post_bots_ok(self):
        data = self._test_post_list_ok(self._telegram_bot_list_url(), TelegramBot, {'token': self.mytoken, 'enabled': 'True'})
        new_bot = TelegramBot.objects.get(token=self.mytoken)
        self.assertEqual(new_bot.token, self.mytoken)
        self.assertTrue(new_bot.enabled)
        self.assertTelegramBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], 
                               data['info']['username'], data['info']['first_name'], data['info']['last_name'], new_bot)
        
    def test_telegram_post_bots_with_no_enabled_field(self):
        data = self._test_post_list_ok(self._telegram_bot_list_url(), TelegramBot, {'token': self.mytoken})
        new_bot = TelegramBot.objects.get(token=self.mytoken)
        self.assertEqual(new_bot.token, self.mytoken)
        self.assertTrue(new_bot.enabled)
        self.assertTelegramBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], 
                               data['info']['username'], data['info']['first_name'], data['info']['last_name'], new_bot)
        
    def test_post_telegram_bots_token_not_valid(self):
        TelegramBot.objects.all().delete()
        response = self.client.post(self._telegram_bot_list_url(),
                                    data=json.dumps({"token": 'invalidtoken', "enabled": True}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a valid token', response.data['token'][0])
        self.assertEqual(TelegramBot.objects.count(), 0)
    
    def test_post_telegram_bots_token_not_exists_in_telegram(self):
        TelegramBot.objects.all().delete()
        response = self.client.post(self._telegram_bot_list_url(),
                                    data=json.dumps({"token": self.mytoken + 'a', "enabled": True}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Telegram Error', response.data['error'])
        self.assertEqual(TelegramBot.objects.count(), 0)
        
    def test_post_telegram_bots_not_auth(self):
        self._test_post_list_not_auth(self._telegram_bot_list_url(), {'token': self.mytoken, 'enabled': 'True'})
        
    def test_get_telegram_bot_ok(self):
        data = self._test_get_detail_ok(self._telegram_bot_detail_url())
        self.assertTelegramBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], data['info']['username'],
                               data['info']['first_name'], data['info']['last_name'])
        
    def test_get_telegram_bot_not_auth(self):
        self._test_get_detail_not_auth(self._telegram_bot_detail_url())
        
    def test_get_telegram_bot_not_found(self):
        self._test_get_detail_not_found(self._telegram_bot_detail_url(telegram_bot_pk=self.unlikely_id))
        
    def test_put_telegram_bot_ok(self):
        data = self._test_put_detail_ok(self._telegram_bot_detail_url(), {'enabled': 'False'}, TelegramBotDetail, self.bot.pk, self.bot.telegram_bot.pk)
        updated = TelegramBot.objects.get(pk=self.bot.telegram_bot.pk)
        self.assertFalse(updated.enabled)
        self.assertTelegramBot(data['id'], data['created_at'], data['updated_at'], data['token'], data['enabled'], 
                               data['info']['username'], data['info']['first_name'], data['info']['last_name'], updated)

    def test_put_telegram_bot_not_auth(self):
        self._test_put_detail_not_auth(self._telegram_bot_detail_url(), 
                                       {'token': self.mytoken, 'enabled': 'False'}, TelegramBotDetail, self.bot.pk, self.bot.telegram_bot.pk)
        
    def test_put_telegram_bot_not_found(self):
        self._test_put_detail_not_found(self._telegram_bot_detail_url(telegram_bot_pk=self.unlikely_id), 
                                        {'token': self.mytoken, 'enabled': 'False'}, TelegramBotDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_telegram_bot_ok(self):
        self._test_delete_detail_ok(self._telegram_bot_detail_url(), TelegramBotDetail, self.bot.pk, self.bot.telegram_bot.pk)
        self.assertEqual(TelegramBot.objects.count(), 0)
        
    def test_delete_telegram_bot_not_auth(self):
        self._test_delete_detail_not_auth(self._telegram_bot_detail_url(), TelegramBotDetail, self.bot.pk, self.bot.telegram_bot.pk)
        
    def test_delete_telegram_bot_not_found(self):
        self._test_delete_detail_not_found(self._telegram_bot_detail_url(telegram_bot_pk=self.unlikely_id), TelegramBotDetail, self.bot.pk, self.unlikely_id)
        
        
class TestKikBotAPI(BaseTestAPI):
    
    def assertKikBot(self, id, created_at, updated_at, api_key, enabled, username, kik_bot=None):
        if not kik_bot:
            kik_bot = self.bot.kik_bot
        self.assertEqual(kik_bot.api_key, api_key)
        self.assertEqual(kik_bot.enabled, enabled)
        self.assertEqual(kik_bot.username, username)
        self.assertMicrobotModel(id, created_at, updated_at, kik_bot)
        
    def _kik_bot_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/kik/' % (self.api, bot_pk)
        
    def _kik_bot_detail_url(self, bot_pk=None, kik_bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not kik_bot_pk:
            kik_bot_pk = self.bot.kik_bot.pk
        return '%s/bots/%s/kik/%s/' % (self.api, bot_pk, kik_bot_pk)
    
    def test_get_kik_bots_ok(self):
        data = self._test_get_list_ok(self._kik_bot_list_url())
        self.assertKikBot(data['id'], data['created_at'], data['updated_at'], data['api_key'], data['enabled'], data['username'], None)
        
    def test_get_kik_bots_not_auth(self):
        self._test_get_list_not_auth(self._kik_bot_list_url())
        
    def test_kik_post_bots_ok(self):
        data = self._test_post_list_ok(self._kik_bot_list_url(), KikBot, {'api_key': self.my_api_key, 'username': self.my_username, 'enabled': 'True'})
        new_bot = KikBot.objects.get(api_key=self.my_api_key, username=self.my_username)
        self.assertEqual(new_bot.api_key, self.my_api_key)
        self.assertEqual(new_bot.username, self.my_username)
        self.assertTrue(new_bot.enabled)
        self.assertKikBot(data['id'], data['created_at'], data['updated_at'], data['api_key'], data['enabled'], 
                          data['username'], new_bot)
        
    def test_kik_post_bots_ok_with_no_enabled_field(self):
        data = self._test_post_list_ok(self._kik_bot_list_url(), KikBot, {'api_key': self.my_api_key, 'username': self.my_username})
        new_bot = KikBot.objects.get(api_key=self.my_api_key, username=self.my_username)
        self.assertEqual(new_bot.api_key, self.my_api_key)
        self.assertEqual(new_bot.username, self.my_username)
        self.assertTrue(new_bot.enabled)
        self.assertKikBot(data['id'], data['created_at'], data['updated_at'], data['api_key'], data['enabled'], 
                          data['username'], new_bot)
    
    def test_post_kik_bots_api_not_exists_in_kik(self):
        TelegramBot.objects.all().delete()
        response = self.client.post(self._kik_bot_list_url(),
                                    data=json.dumps({"api_key": self.my_api_key + 'a', "enabled": True, 'username': self.my_username}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Kik Error', response.data['error'])
        self.assertEqual(TelegramBot.objects.count(), 0)  
        
    def test_post_kik_bots_user_not_exists_in_kik(self):
        TelegramBot.objects.all().delete()
        response = self.client.post(self._kik_bot_list_url(),
                                    data=json.dumps({"api_key": self.my_api_key, "enabled": True, 'username': self.my_username + 'o'}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Kik Error', response.data['error'])
        self.assertEqual(TelegramBot.objects.count(), 0)
        
    def test_post_kik_bots_not_auth(self):
        self._test_post_list_not_auth(self._kik_bot_list_url(), {'api_key': self.my_api_key, 'enabled': 'True', 'username': self.my_username})
        
    def test_get_kik_bot_ok(self):
        data = self._test_get_detail_ok(self._kik_bot_detail_url())
        self.assertKikBot(data['id'], data['created_at'], data['updated_at'], data['api_key'], data['enabled'], data['username'],)
        
    def test_get_kik_bot_not_auth(self):
        self._test_get_detail_not_auth(self._kik_bot_detail_url())
        
    def test_get_kik_bot_not_found(self):
        self._test_get_detail_not_found(self._kik_bot_detail_url(kik_bot_pk=self.unlikely_id))
        
    def test_put_kik_bot_ok(self):
        data = self._test_put_detail_ok(self._kik_bot_detail_url(), {'enabled': 'False'}, KikBotDetail, self.bot.pk, self.bot.kik_bot.pk)
        updated = KikBot.objects.get(pk=self.bot.kik_bot.pk)
        self.assertFalse(updated.enabled)
        self.assertKikBot(data['id'], data['created_at'], data['updated_at'], data['api_key'], data['enabled'], 
                          data['username'], updated)

    def test_put_kik_bot_not_auth(self):
        self._test_put_detail_not_auth(self._kik_bot_detail_url(), 
                                       {'api_key': self.my_api_key, 'username': self.my_username, 'enabled': 'False'}, 
                                       KikBotDetail, self.bot.pk, self.bot.kik_bot.pk)
        
    def test_put_kik_bot_not_found(self):
        self._test_put_detail_not_found(self._kik_bot_detail_url(kik_bot_pk=self.unlikely_id), 
                                        {'api_key': self.my_api_key, 'username': self.my_username, 'enabled': 'False'}, 
                                        KikBotDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_kik_bot_ok(self):
        self._test_delete_detail_ok(self._kik_bot_detail_url(), KikBotDetail, self.bot.pk, self.bot.kik_bot.pk)
        self.assertEqual(KikBot.objects.count(), 0)
        
    def test_delete_kik_bot_not_auth(self):
        self._test_delete_detail_not_auth(self._kik_bot_detail_url(), KikBotDetail, self.bot.pk, self.bot.kik_bot.pk)
        
    def test_delete_kik_bot_not_found(self):
        self._test_delete_detail_not_found(self._kik_bot_detail_url(kik_bot_pk=self.unlikely_id), KikBotDetail, self.bot.pk, self.unlikely_id)