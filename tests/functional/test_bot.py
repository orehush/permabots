#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import TelegramBot
from microbot.test import testcases
from django.core.urlresolvers import reverse
from rest_framework import status
from django.core.exceptions import ValidationError
from django.test import override_settings
try:
    from unittest import mock
except ImportError:
    import mock  # noqa

class TestBot(testcases.BaseTestBot):
       
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
        response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
          
    def test_bot_disabled(self):
        self.bot.telegram_bot.enabled = False
        self.bot.telegram_bot.save()
        with mock.patch("microbot.tasks.handle_update.delay", callable=mock.MagicMock()) as mock_send:
            response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(0, mock_send.call_count)
        
    def test_not_valid_update(self):
        del self.update.message
        response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
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
    
    @override_settings(MICROBOT_WEBHOOK_DOMAIN='manualdomain.com')
    def test_webhook_domain_manually(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.telegram_bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn('manualdomain.com', kwargs['webhook_url'])