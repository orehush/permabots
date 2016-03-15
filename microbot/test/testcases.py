#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from microbot.models import Update
from telegram import User
from microbot.test import factories
from django.core.urlresolvers import reverse
from rest_framework import status
from telegram.replykeyboardhide import ReplyKeyboardHide
try:
    from unittest import mock
except ImportError:
    import mock  # noqa


class BaseTestBot(TestCase):    

    def setUp(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()):
            with mock.patch("telegram.bot.Bot.getMe", callable=mock.MagicMock()) as mock_get_me:
                user_dict = {'username': u'Microbot_test_bot', 'first_name': u'Microbot_test', 'id': 204840063}
                mock_get_me.return_value = User(**user_dict)
                self.bot = factories.BotFactory()
                self.webhook_url = reverse('microbot:telegrambot', kwargs={'token': self.bot.token})
                self.update = factories.UpdateLibFactory()
                self.kwargs = {'content_type': 'application/json', }

    def assertUser(self, model_user, user):
        self.assertEqual(model_user.id, user.id)
        self.assertEqual(model_user.first_name, user.first_name)
        self.assertEqual(model_user.last_name, user.last_name)
        self.assertEqual(model_user.username, user.username)
        
    def assertChat(self, model_chat, chat):        
        self.assertEqual(model_chat.id, chat.id)
        self.assertEqual(model_chat.type, chat.type)
        self.assertEqual(model_chat.title, chat.title)
        self.assertEqual(model_chat.username, chat.username)
        self.assertEqual(model_chat.first_name, chat.first_name)
        self.assertEqual(model_chat.last_name, chat.last_name)
        
    def assertMessage(self, model_message, message):        
        self.assertEqual(model_message.message_id, message.message_id)
        self.assertUser(model_message.from_user, message.from_user)
        self.assertChat(model_message.chat, message.chat)
        #  TODO: problems with UTCs
        #  self.assertEqual(model_message.date, message.date)
        self.assertEqual(model_message.text, message.text)
        
    def assertUpdate(self, model_update, update):
        self.assertEqual(model_update.update_id, update.update_id)
        self.assertMessage(model_update.message, update.message)
        
    def assertInKeyboard(self, button, keyboard):
        found = False
        for line in keyboard:
            if button in line:
                found = True
                break
        self.assertTrue(found)
        
    def assertBotResponse(self, mock_send, command):
        args, kwargs = mock_send.call_args
        self.assertEqual(1, mock_send.call_count)
        self.assertEqual(kwargs['chat_id'], self.update.message.chat.id)
        self.assertEqual(kwargs['parse_mode'], command['out']['parse_mode'])
        if not command['out']['reply_markup']:
            self.assertTrue(isinstance(kwargs['reply_markup'], ReplyKeyboardHide))
        else:
            self.assertInKeyboard(command['out']['reply_markup'], kwargs['reply_markup'].keyboard)
                
        self.assertIn(command['out']['text'], kwargs['text'].decode('utf-8'))
        
    def _test_message(self, action, update=None, number=1, no_handler=False):
        if not update:
            update = self.update
        with mock.patch("telegram.bot.Bot.sendMessage", callable=mock.MagicMock()) as mock_send:
            if 'in' in action:
                update.message.text = action['in']
            response = self.client.post(self.webhook_url, update.to_json(), **self.kwargs)
            #  Check response 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            #  Check  
            if no_handler:
                self.assertEqual(0, mock_send.call_count)
            else:
                self.assertBotResponse(mock_send, action)
            self.assertEqual(number, Update.objects.count())
            self.assertUpdate(Update.objects.get(update_id=update.update_id), update)       