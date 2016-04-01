#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot
from rest_framework import status
from microbot.views import BotDetail
import json
from tests.api.base import BaseTestAPI

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
        
    def test_post_bots_token_not_valid(self):
        Bot.objects.all().delete()
        response = self.client.post(self._bot_list_url(),
                                    data=json.dumps({"token": 'invalidtoken', "enabled": True}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a valid token', response.data['token'][0])
        self.assertEqual(Bot.objects.count(), 0)
    
    def test_post_bots_token_not_exists_in_telegram(self):
        Bot.objects.all().delete()
        response = self.client.post(self._bot_list_url(),
                                    data=json.dumps({"token": self.mytoken + 'a', "enabled": True}), 
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self._gen_token(self.bot.owner.auth_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Telegram Error', response.data['error'])
        self.assertEqual(Bot.objects.count(), 0)
        
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
        self._test_put_detail_ok(self._bot_detail_url(), {'enabled': 'False'}, BotDetail, self.bot.pk)
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