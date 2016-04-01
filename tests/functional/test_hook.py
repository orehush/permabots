#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import EnvironmentVar, Hook
from microbot.test import factories, testcases
from rest_framework import status
try:
    from unittest import mock
except ImportError:
    import mock  # noqa


class TestHook(testcases.BaseTestBot):   
    
    hook_name = {'in': 'key1',
                 'out': {'parse_mode': 'HTML',
                         'reply_markup': 'juan',
                         'text': '<b>juan</b>'
                         }
                 }
    
    hook_keyboard = {'in': 'key1',
                     'out': {'parse_mode': 'HTML',
                             'reply_markup': 'Go back',
                             'text': '<b>juan</b>'
                             }
                     }
    
    def setUp(self):
        super(TestHook, self).setUp()        
        EnvironmentVar.objects.create(bot=self.bot,
                                      key="back", 
                                      value="Go back")
        self.response = factories.ResponseFactory(text_template='<b>{{data.name}}</b>',
                                                  keyboard_template='[["{{data.name}}"]]')
        self.hook = factories.HookFactory(bot=self.bot,
                                          key="key1",
                                          response=self.response)
        self.recipient = factories.RecipientFactory(hook=self.hook)
        
    def test_generate_key(self):
        new_response = factories.ResponseFactory(text_template='<b>{{data.name}}</b>',
                                                 keyboard_template='[["{{data.name}}"]]')
        hook = Hook.objects.create(bot=self.bot,
                                   response=new_response)
        self.assertNotEqual(None, hook.key)
             
    def test_no_hook(self):
        self._test_hook({'in': "keynotfound"}, {}, no_hook=True, auth=self._gen_token(self.bot.owner.auth_token))
        
    def test_hook_disabled(self):
        self.hook.enabled = False
        self.hook.save()
        self._test_hook(self.hook_name, '{"name": "juan"}', no_hook=True,
                        auth=self._gen_token(self.hook.bot.owner.auth_token))
        
    def test_hook(self):
        self._test_hook(self.hook_name, '{"name": "juan"}', num_recipients=1, recipients=[self.recipient.chat_id],
                        auth=self._gen_token(self.hook.bot.owner.auth_token))
        
    def test_hook_keyboard(self):
        self.response.keyboard_template = [["{{data.name}}"], ["{{env.back}}"]]
        self.response.save()
        self._test_hook(self.hook_keyboard, '{"name": "juan"}', num_recipients=1, recipients=[self.recipient.chat_id],
                        auth=self._gen_token(self.hook.bot.owner.auth_token))
        
    def test_hook_multiple_recipients(self):
        new_recipient = factories.RecipientFactory(hook=self.hook)
        self._test_hook(self.hook_name, '{"name": "juan"}', num_recipients=2, recipients=[self.recipient.chat_id, new_recipient.chat_id],
                        auth=self._gen_token(self.hook.bot.owner.auth_token))
        
    def test_not_auth(self):
        self._test_hook(self.hook_name, '{"name": "juan"}', num_recipients=1, recipients=[self.recipient.chat_id],
                        auth=self._gen_token("notoken"), status_to_check=status.HTTP_401_UNAUTHORIZED)