#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, TelegramBot, KikBot, MessengerBot
from microbot.test import testcases
from django.core.urlresolvers import reverse
from rest_framework import status
from django.core.exceptions import ValidationError
from django.test import override_settings
try:
    from unittest import mock
except ImportError:
    import mock  # noqa
  
class TestTelegramBot(testcases.BaseTestBot):
       
    def test_enable_webhook(self):
        self.assertTrue(self.bot.telegram_bot.enabled)
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.telegram_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn(reverse('microbot:telegrambot', kwargs={'hook_id': self.bot.telegram_bot.hook_id}), 
                          kwargs['webhook_url'])
               
    def test_disable_webhook(self):
        self.bot.telegram_bot.enabled = False
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.telegram_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertEqual(None, kwargs['webhook_url'])
               
    def test_bot_user_api(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()):
            self.bot.telegram_bot.user_api = None
            self.bot.telegram_bot.save()
            self.assertEqual(self.bot.telegram_bot.user_api.first_name, u'Microbot_test')
            self.assertEqual(self.bot.telegram_bot.user_api.username, u'Microbot_test_bot')
               
    def test_no_bot_associated(self):
        TelegramBot.objects.all().delete()
        self.assertEqual(0, TelegramBot.objects.count())
        response = self.client.post(self.telegram_webhook_url, self.telegram_update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
          
    def test_bot_disabled(self):
        self.bot.telegram_bot.enabled = False
        self.bot.telegram_bot.save()
        with mock.patch("microbot.tasks.handle_update.delay", callable=mock.MagicMock()) as mock_send:
            response = self.client.post(self.telegram_webhook_url, self.telegram_update.to_json(), **self.kwargs)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(0, mock_send.call_count)
        
    def test_not_valid_update(self):
        del self.telegram_update.message
        response = self.client.post(self.telegram_webhook_url, self.telegram_update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        
    def test_not_valid_bot_token(self):
        self.assertRaises(ValidationError, TelegramBot.objects.create, token="asdasd")
        
    def test_webhook_domain_auto_site(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.telegram_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn(current_site.domain, kwargs['webhook_url'])
            
    def test_delete_integrations(self):
        self.bot.delete()
        self.assertEqual(0, Bot.objects.count())
        self.assertEqual(0, TelegramBot.objects.count())
        self.assertEqual(0, KikBot.objects.count())
    
    @override_settings(MICROBOT_WEBHOOK_DOMAIN='manualdomain.com')
    def test_webhook_domain_manually(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.telegram_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn('manualdomain.com', kwargs['webhook_url'])
            
            
class TestKikBot(testcases.KikTestBot):
    set_webhook_call = "kik.api.KikApi.set_configuration"
    
    def test_enable_webhook(self):
        self.assertTrue(self.bot.kik_bot.enabled)
        with mock.patch(self.set_webhook_call, callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.kik_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn(reverse('microbot:kikbot', kwargs={'hook_id': self.bot.kik_bot.hook_id}), 
                          args[0].webhook)
               
    def test_disable_webhook(self):
        self.bot.kik_bot.enabled = False
        with mock.patch(self.set_webhook_call, callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.kik_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertEqual("https://example.com", args[0].webhook)
               
    def test_no_bot_associated(self):
        KikBot.objects.all().delete()
        self.assertEqual(0, KikBot.objects.count())
        response = self.client.post(self.kik_webhook_url, self.to_send(self.kik_messages), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
          
    def test_bot_disabled(self):
        self.bot.kik_bot.enabled = False
        self.bot.kik_bot.save()
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()) as mock_verify:
            mock_verify.return_value = True
            with mock.patch("microbot.tasks.handle_message.delay", callable=mock.MagicMock()) as mock_send:
                response = self.client.post(self.kik_webhook_url, self.to_send(self.kik_messages), **self.kwargs)
                self.assertEqual(status.HTTP_200_OK, response.status_code)
                self.assertEqual(0, mock_send.call_count)
        
    def test_webhook_domain_auto_site(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        with mock.patch(self.set_webhook_call, callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.kik_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn(current_site.domain, args[0].webhook)
    
    @override_settings(MICROBOT_WEBHOOK_DOMAIN='manualdomain.com')
    def test_webhook_domain_manually(self):
        with mock.patch(self.set_webhook_call, callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.kik_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn('manualdomain.com', args[0].webhook)    
            
            
class TestMessengerBot(testcases.MessengerTestBot):
    set_webhook_call = "messengerbot.MessengerClient.subscribe_app"
    
    def test_subscribe(self):
        self.assertTrue(self.bot.messenger_bot.enabled)
        with mock.patch(self.set_webhook_call, callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.messenger_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
               
    def test_no_bot_associated(self):
        MessengerBot.objects.all().delete()
        self.assertEqual(0, MessengerBot.objects.count())
        response = self.client.post(self.messenger_webhook_url, self.to_send(self.messenger_webhook_message), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
          
    def test_bot_disabled(self):
        self.bot.messenger_bot.enabled = False
        self.bot.messenger_bot.save()
        with mock.patch("microbot.tasks.handle_messenger_message.delay", callable=mock.MagicMock()) as mock_send:
            response = self.client.post(self.messenger_webhook_url, self.to_send(self.messenger_webhook_message), **self.kwargs)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(0, mock_send.call_count)
            
    def test_bot_verify_ok(self):
        response = self.client.get(self.messenger_webhook_url, {'hub.mode': 'subscribe', 'hub.challenge': 12345, 'hub.verify_token': self.bot.messenger_bot.id})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, 12345)
        
    def test_bot_verify_not_ok(self):
        response = self.client.get(self.messenger_webhook_url, {'hub.mode': 'subscribe', 'hub.challenge': 12345, 'hub.verify_token': 'other_id'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('Error', response.data)    
