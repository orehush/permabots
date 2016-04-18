#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from microbot.models import TelegramUpdate
from telegram import User
from microbot.test import factories
from django.core.urlresolvers import reverse
from rest_framework import status
from telegram.replykeyboardhide import ReplyKeyboardHide
from microbot.models.kik_api import KikMessage
import json
try:
    from unittest import mock
except ImportError:
    import mock  # noqa


class BaseTestBot(TestCase):    
    
    def _gen_token(self, token):
        return 'Token  %s' % str(token)

    def setUp(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()):
            with mock.patch("kik.api.KikApi.set_configuration", callable=mock.MagicMock()):
                with mock.patch("telegram.bot.Bot.getMe", callable=mock.MagicMock()) as mock_get_me:
                    user_dict = {'username': u'Microbot_test_bot', 'first_name': u'Microbot_test', 'id': 204840063}
                    mock_get_me.return_value = User(**user_dict)
                    self.bot = factories.BotFactory()
                    self.telegram_webhook_url = reverse('microbot:telegrambot', kwargs={'hook_id': self.bot.telegram_bot.hook_id})
                    self.kik_webhook_url = reverse('microbot:kikbot', kwargs={'hook_id': self.bot.kik_bot.hook_id})
                    self.telegram_update = factories.TelegramUpdateLibFactory()
                    self.kik_message = factories.KikMessageLibFactory()
                    self.kik_message.participants = [self.kik_message.from_user]
                    self.kik_messages = {'messages': [self.kik_message]}
                    self.kwargs = {'content_type': 'application/json', }
                                        
    def _test_message(self, action, message_api=None, number=1, no_handler=False):
        if not message_api:
            message_api = self.message_api
            
        with mock.patch(self.send_message_to_patch, callable=mock.MagicMock()) as mock_send:
            if 'in' in action:
                self.set_text(action['in'], message_api)
            response = self.client.post(self.webhook_url, self.to_send(message_api), **self.kwargs)
            #  Check response 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            #  Check  
            if no_handler:
                self.assertEqual(0, mock_send.call_count)
            else:
                self.assertBotResponse(mock_send, action)
            self.assertAPI(number, message_api)
            
    def _test_hook(self, action, data, no_hook=False, num_recipients=1, recipients=[], auth=None, status_to_check=None,
                   error_to_check=None):
        with mock.patch(self.send_message_to_patch, callable=mock.MagicMock()) as mock_send:
            hook_url = reverse('microbot:hook', kwargs={'key': action['in']})
            if auth:
                response = self.client.post(hook_url, data, HTTP_AUTHORIZATION=auth, **self.kwargs)
            else:
                response = self.client.post(hook_url, data, **self.kwargs)
            if no_hook:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            else:
                if status_to_check:
                    self.assertEqual(response.status_code, status_to_check)
                    if error_to_check:
                        self.assertIn(error_to_check, response.data)
                else:
                    #  Check response 200 OK
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertBotResponse(mock_send, action, num=num_recipients, recipients=recipients)
                    
class TelegramTestBot(BaseTestBot):
      
    def setUp(self):
        super(TelegramTestBot, self).setUp()
        self.send_message_to_patch = 'telegram.bot.Bot.sendMessage'
        self.webhook_url = self.telegram_webhook_url
        self.message_api = self.telegram_update

    def set_text(self, text, update):
        update.message.text = text
        
    def to_send(self, update):
        return update.to_json()
    
    def assertTelegramUser(self, model_user, user):
        self.assertEqual(model_user.id, user.id)
        self.assertEqual(model_user.first_name, user.first_name)
        self.assertEqual(model_user.last_name, user.last_name)
        self.assertEqual(model_user.username, user.username)
        
    def assertTelegramChat(self, model_chat, chat):        
        self.assertEqual(model_chat.id, chat.id)
        self.assertEqual(model_chat.type, chat.type)
        self.assertEqual(model_chat.title, chat.title)
        self.assertEqual(model_chat.username, chat.username)
        self.assertEqual(model_chat.first_name, chat.first_name)
        self.assertEqual(model_chat.last_name, chat.last_name)
        
    def assertTelegramMessage(self, model_message, message):        
        self.assertEqual(model_message.message_id, message.message_id)
        self.assertTelegramUser(model_message.from_user, message.from_user)
        self.assertTelegramChat(model_message.chat, message.chat)
        #  TODO: problems with UTCs
        #  self.assertEqual(model_message.date, message.date)
        self.assertEqual(model_message.text, message.text)
        
    def assertTelegramUpdate(self, model_update, update):
        self.assertEqual(model_update.update_id, update.update_id)
        self.assertTelegramMessage(model_update.message, update.message)
             
    def assertInTelegramKeyboard(self, button, keyboard):
        found = False
        for line in keyboard:
            if button in line:
                found = True
                break
        self.assertTrue(found)
        
    def assertBotResponse(self, mock_send, command, num=1, recipients=[]):
        self.assertEqual(num, mock_send.call_count)
        for call_args in mock_send.call_args_list:
            args, kwargs = call_args
            if not recipients:    
                self.assertEqual(kwargs['chat_id'], self.telegram_update.message.chat.id)
            else:
                recipients.remove(kwargs['chat_id'])                
            self.assertEqual(kwargs['parse_mode'], command['out']['parse_mode'])
            if not command['out']['reply_markup']:
                self.assertTrue(isinstance(kwargs['reply_markup'], ReplyKeyboardHide))
            else:
                self.assertInTelegramKeyboard(command['out']['reply_markup'], kwargs['reply_markup'].keyboard)
                
            self.assertIn(command['out']['text'], kwargs['text'].decode('utf-8'))
        self.assertEqual([], recipients)

    def assertAPI(self, number, message_api):
        self.assertEqual(number, TelegramUpdate.objects.count())
        self.assertTelegramUpdate(TelegramUpdate.objects.get(update_id=message_api.update_id), message_api)   
        
        
class KikTestBot(BaseTestBot):
    
    def setUp(self):
        super(KikTestBot, self).setUp()
        self.send_message_to_patch = 'kik.api.KikApi.send_messages'
        self.webhook_url = self.kik_webhook_url
        self.message_api = self.kik_messages

    def set_text(self, text, update):
        update['messages'][0].body = text
        
    def to_send(self, messages):
        from time import mktime
        message = messages['messages'][0]
        if message.timestamp:
            message.timestamp = int(mktime(message.timestamp.timetuple()))
        message.id = str(message.id)
        return json.dumps({'messages': [message.to_json()]})
        
    def assertKikMessage(self, model_message, message):        
        self.assertEqual(str(model_message.message_id), message.id)
        self.assertEqual(model_message.from_user.username, message.from_user)
        self.assertEqual(model_message.chat.id, message.chat_id)
        if message.participants:
            self.assertEqual([participant.username for participant in model_message.chat.participants.all()], message.participants)
        else:
            self.assertEqual(model_message.chat.participants.count(), 0)
        #  TODO: problems with UTCs
        #  self.assertEqual(model_message.date, message.date)
        self.assertEqual(model_message.body, message.body)
        
    def assertInKikKeyboard(self, button, keyboard):
        found = False
        for response in keyboard.responses:
            if button in response.body:
                found = True
                break
        self.assertTrue(found)
        
    def assertBotResponse(self, mock_send, command, num=1, recipients=[]):
        self.assertEqual(num, mock_send.call_count)
        for call_args in mock_send.call_args_list:
            args, kwargs = call_args
            message = args[0][0]
            if not recipients:    
                self.assertEqual(message.chat_id, self.kik_message.chat_id)
            else:
                recipients.remove(kwargs['chat_id'])
                
            if not command['out']['reply_markup']:
                self.assertEqual(message.keyboard, [])
            else:
                self.assertInKikKeyboard(command['out']['reply_markup'], message.keyboards[0])
            self.assertIn(command['out']['body'], message.body.decode('utf-8'))
        self.assertEqual([], recipients)

    def assertAPI(self, number, message_api):
        self.assertEqual(number, KikMessage.objects.count())
        self.assertKikMessage(KikMessage.objects.get(message_id=message_api['messages'][0].id), message_api['messages'][0])   