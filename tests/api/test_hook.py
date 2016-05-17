#!/usr/bin/env python
# -*- coding: utf-8 -*-
from permabots.models import Hook, TelegramRecipient, KikRecipient, MessengerRecipient
from permabots.test import factories
from permabots.views import HandlerDetail, HookDetail, TelegramRecipientDetail, KikRecipientDetail, MessengerRecipientDetail
from tests.api.base import BaseTestAPI

class TestHookAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.TelegramRecipientFactory(hook=self.hook)
        
    def _hook_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/hooks/' % (self.api, bot_pk)
    
    def _hook_detail_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/' % (self.api, bot_pk, hook_pk)

    def assertHook(self, id, created_at, updated_at, name, response_text_template, response_keyboard_template, enabled, 
                   telegram_recipients, kik_recipients, hook=None):
        if not hook:
            hook = self.hook
        self.assertEqual(hook.name, name)
        self.assertEqual(hook.response.text_template, response_text_template)
        self.assertEqual(hook.response.keyboard_template, response_keyboard_template)
        self.assertEqual(hook.enabled, enabled)
        self.assertPermabotsModel(id, created_at, updated_at, hook)
        if telegram_recipients:
            self.assertEqual(hook.telegram_recipients.count(), len(telegram_recipients))
            # check recipients
            for recipient in telegram_recipients:
                self.assertEqual(TelegramRecipient.objects.get(chat_id=recipient['chat_id']).chat_id, recipient['chat_id'])
                self.assertEqual(TelegramRecipient.objects.get(chat_id=recipient['chat_id']).name, recipient['name'])
        
        if kik_recipients:
            self.assertEqual(hook.kik_recipients.count(), len(kik_recipients))
            # check recipients
            for recipient in kik_recipients:
                self.assertEqual(KikRecipient.objects.get(chat_id=recipient['chat_id']).chat_id, recipient['chat_id'])
                self.assertEqual(KikRecipient.objects.get(chat_id=recipient['chat_id']).name, recipient['name'])
        
    def test_get_hooks_ok(self):
        data = self._test_get_list_ok(self._hook_list_url())
        self.assertHook(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                        data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                        data[0]['enabled'], data[0]['telegram_recipients'], data[0]['kik_recipients'])
        
    def test_get_hooks_not_auth(self):
        self._test_get_list_not_auth(self._hook_list_url())
        
    def test_post_hooks_ok(self):
        data = {'name': self.hook.name, 'response': {'text_template': self.hook.response.text_template,
                                                     'keyboard_template': self.hook.response.keyboard_template},
                'enabled': False, 
                }
        data = self._test_post_list_ok(self._hook_list_url(), Hook, data)
        new_hook = Hook.objects.filter(bot=self.bot)[0]
        self.assertHook(None, self.hook.created_at, self.hook.updated_at, self.hook.name, self.hook.response.text_template, 
                        self.hook.response.keyboard_template,
                        False, None, None, hook=new_hook)
        self.assertHook(data['id'], data['created_at'], data['updated_at'], data['name'], 
                        data['response']['text_template'], data['response']['keyboard_template'],
                        data['enabled'], data['telegram_recipients'], data['kik_recipients'], new_hook)
        
    def test_post_hooks_validation_error(self):
        data = {'name': self.hook.name, 'response': {'text_template': '<b>{{a</b',
                                                     'keyboard_template': '["{{a}","asdasd"]]'},
                'enabled': False, 
                }
        errors = self._test_post_list_validation_error(self._hook_list_url(), Hook, data)
        self.assertNotEqual(None, errors['response']['text_template'][0])
        self.assertNotEqual(None, errors['response']['text_template'][1])
        self.assertNotEqual(None, errors['response']['keyboard_template'][0])

    def test_post_hooks_not_auth(self):
        data = {'name': self.hook.name, 'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False}
        self._test_post_list_not_auth(self._hook_list_url(), data)
        
    def test_get_hook_ok(self):
        data = self._test_get_detail_ok(self._hook_detail_url())
        self.assertHook(data['id'], data['created_at'], data['updated_at'], data['name'], 
                        data['response']['text_template'], data['response']['keyboard_template'], data['enabled'],
                        data['telegram_recipients'], data['kik_recipients'])
        
    def test_get_hook_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_detail_url)
        
    def test_get_hook_not_auth(self):
        self._test_get_detail_not_auth(self._hook_detail_url())
        
    def test_get_hook_not_found(self):
        self._test_get_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id))
        
    def test_put_hook_ok(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                             'keyboard_template': self.hook.response.keyboard_template}, 
                'enabled': False, 'name': self.hook.name,
                }
        data = self._test_put_detail_ok(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        updated = Hook.objects.get(pk=self.hook.pk)
        self.assertEqual(updated.enabled, False)
        self.assertHook(data['id'], data['created_at'], data['updated_at'], data['name'], 
                        data['response']['text_template'], data['response']['keyboard_template'],
                        data['enabled'], data['telegram_recipients'], data['kik_recipients'], updated)
        
    def test_put_hook_validation_error(self):
        data = {'response': {'text_template': '{{asd}</code>',
                             'keyboard_template': '[["{{asd}","asdasd"]'}, 
                'enabled': False, 'name': self.hook.name,
                }
        response = self._test_put_detail_validation_error(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        self.assertNotEqual(None, response.data['response']['text_template'][0]) 
        self.assertNotEqual(None, response.data['response']['text_template'][1]) 
        self.assertNotEqual(None, response.data['response']['keyboard_template'][0])  
        
    def test_put_hook_only_name_ok(self):
        data = {'name': "new_name",
                }
        self._test_put_detail_ok(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        self.assertEqual(Hook.objects.get(pk=self.hook.pk).name, "new_name")
        
    def test_put_hook_only_enabled_ok(self):
        data = {'enabled': False,
                }
        self._test_put_detail_ok(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        self.assertEqual(Hook.objects.get(pk=self.hook.pk).enabled, False)
        
    def test_put_hook_only_response_text_ok(self):
        data = {'response': {'text_template': 'new_text_template'}}
        self._test_put_detail_ok(self._hook_detail_url(), data, HookDetail, self.bot.pk, self.hook.pk)
        self.assertEqual(Hook.objects.get(pk=self.hook.pk).response.text_template, 'new_text_template')
        
    def test_put_hook_from_other_bot(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                             'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                'recipients': [{'chat_id': recipient.chat_id, 'name': recipient.name} for recipient in self.hook.telegram_recipients.all()]
                }
        self._test_put_detail_from_other_bot(self._hook_detail_url, data, HookDetail, self.hook.pk)
        
    def test_put_hook_not_auth(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                }
        self._test_put_detail_not_auth(self._hook_detail_url(), data, HandlerDetail, self.bot.pk, self.hook.pk)
        
    def test_put_hook_not_found(self):
        data = {'response': {'text_template': self.hook.response.text_template,
                'keyboard_template': self.hook.response.keyboard_template}, 'enabled': False, 'name': self.hook.name,
                }
        self._test_put_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id), data, HookDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_hook_ok(self):
        self._test_delete_detail_ok(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_detail_url, HookDetail, self.hook.pk)
        
    def test_delete_hook_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_detail_url(), HookDetail, self.bot.pk, self.hook.pk)
        
    def test_delete_hook_not_found(self):
        self._test_delete_detail_not_found(self._hook_detail_url(hook_pk=self.unlikely_id), HookDetail, self.bot.pk, self.unlikely_id)


class TestHookTelegramRecipientAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookTelegramRecipientAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.TelegramRecipientFactory(hook=self.hook)
        
    def _hook_recipient_list_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/recipients/telegram/' % (self.api, bot_pk, hook_pk)
    
    def _hook_recipient_detail_url(self, bot_pk=None, hook_pk=None, recipient_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        if not recipient_pk:
            recipient_pk = self.hook.telegram_recipients.all()[0].pk
        return '%s/bots/%s/hooks/%s/recipients/telegram/%s/' % (self.api, bot_pk, hook_pk, recipient_pk)
    
    def assertRecipient(self, chat_id, name, recipient=None):
        if not recipient:
            recipient = self.hook.telegram_recipients.all()[0]
        self.assertEqual(recipient.chat_id, chat_id)
        self.assertEqual(recipient.name, name)

    def test_get_hook_recipients_ok(self):
        data = self._test_get_list_ok(self._hook_recipient_list_url())
        self.assertRecipient(data[0]['chat_id'], data[0]['name'])
        
    def test_get_hook_recipients_not_auth(self):
        self._test_get_list_not_auth(self._hook_recipient_list_url())
        
    def test_post_hook_recipient_ok(self):
        data = {'chat_id': self.hook.telegram_recipients.all()[0].chat_id, 'name': self.hook.telegram_recipients.all()[0].name}                              
        data = self._test_post_list_ok(self._hook_recipient_list_url(), TelegramRecipient, data)
        new_recipient = TelegramRecipient.objects.filter(hook=self.hook)[0]        
        self.assertRecipient(self.hook.telegram_recipients.all()[0].chat_id, self.hook.telegram_recipients.all()[0].name, recipient=new_recipient)
        self.assertRecipient(data['chat_id'], data['name'], new_recipient)
        
    def test_post_hook_recipient_not_auth(self):
        data = {'chat_id': self.hook.telegram_recipients.all()[0].chat_id, 'name': self.hook.telegram_recipients.all()[0].name}
        self._test_post_list_not_auth(self._hook_recipient_list_url(), data)
        
    def test_get_recipient_ok(self):
        data = self._test_get_detail_ok(self._hook_recipient_detail_url())
        self.assertRecipient(data['chat_id'], data['name'])
        
    def test_get_recipient_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_recipient_detail_url)
        
    def test_get_recipient_not_auth(self):
        self._test_get_detail_not_auth(self._hook_recipient_detail_url())
        
    def test_get_recipient_not_found(self):
        self._test_get_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id))       
        
    def test_put_recipient_ok(self):
        data = {'chat_id': 9999, 'name': 'new_name'} 
        self._test_put_detail_ok(self._hook_recipient_detail_url(), data, TelegramRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        updated = TelegramRecipient.objects.get(pk=self.recipient.pk)
        self.assertEqual(updated.name, 'new_name')
        self.assertEqual(updated.chat_id, 9999)
        self.assertRecipient(data['chat_id'], data['name'], updated)
        
    def test_put_recipient_from_other_bot(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_from_other_bot(self._hook_recipient_detail_url, data, TelegramRecipientDetail, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_auth(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_not_auth(self._hook_recipient_detail_url(), data, TelegramRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_found(self):
        data = {'chat_id': 9999, 'name': 'new_name'}
        self._test_put_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), data, 
                                        TelegramRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)

    def test_delete_recipient_ok(self):
        self._test_delete_detail_ok(self._hook_recipient_detail_url(), TelegramRecipientDetail, 
                                    self.bot.pk, self.hook.pk, self.hook.telegram_recipients.all()[0].pk)
        
    def test_delete_recipient_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_recipient_detail_url, TelegramRecipientDetail, 
                                                self.bot.pk, self.hook.pk, self.hook.telegram_recipients.all()[0].pk)
        
    def test_delete_recipient_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_recipient_detail_url(), TelegramRecipientDetail, 
                                          self.bot.pk, self.hook.pk, self.hook.telegram_recipients.all()[0].pk)
        
    def test_delete_recipient_not_found(self):
        self._test_delete_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), 
                                           TelegramRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)
        
        
class TestHookKikRecipientAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookKikRecipientAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.KikRecipientFactory(hook=self.hook)
        
    def _hook_recipient_list_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/recipients/kik/' % (self.api, bot_pk, hook_pk)
    
    def _hook_recipient_detail_url(self, bot_pk=None, hook_pk=None, recipient_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        if not recipient_pk:
            recipient_pk = self.hook.kik_recipients.all()[0].pk
        return '%s/bots/%s/hooks/%s/recipients/kik/%s/' % (self.api, bot_pk, hook_pk, recipient_pk)
    
    def assertRecipient(self, chat_id, name, username, recipient=None):
        if not recipient:
            recipient = self.hook.kik_recipients.all()[0]
        self.assertEqual(recipient.chat_id, chat_id)
        self.assertEqual(recipient.name, name)
        self.assertEqual(recipient.username, username)

    def test_get_hook_recipients_ok(self):
        data = self._test_get_list_ok(self._hook_recipient_list_url())
        self.assertRecipient(data[0]['chat_id'], data[0]['name'], data[0]['username'])
        
    def test_get_hook_recipients_not_auth(self):
        self._test_get_list_not_auth(self._hook_recipient_list_url())
        
    def test_post_hook_recipient_ok(self):
        data = {'chat_id': self.hook.kik_recipients.all()[0].chat_id, 'name': self.hook.kik_recipients.all()[0].name, 
                'username': self.hook.kik_recipients.all()[0].username}                              
        data = self._test_post_list_ok(self._hook_recipient_list_url(), KikRecipient, data)
        new_recipient = KikRecipient.objects.filter(hook=self.hook)[0]        
        self.assertRecipient(self.hook.kik_recipients.all()[0].chat_id, self.hook.kik_recipients.all()[0].name, 
                             self.hook.kik_recipients.all()[0].username, recipient=new_recipient)
        self.assertRecipient(data['chat_id'], data['name'], data['username'], new_recipient)
        
    def test_post_hook_recipient_not_auth(self):
        data = {'chat_id': self.hook.kik_recipients.all()[0].chat_id, 'name': self.hook.kik_recipients.all()[0].name, 
                'username': self.hook.kik_recipients.all()[0].username}
        self._test_post_list_not_auth(self._hook_recipient_list_url(), data)
        
    def test_get_recipient_ok(self):
        data = self._test_get_detail_ok(self._hook_recipient_detail_url())
        self.assertRecipient(data['chat_id'], data['name'], data['username'])
        
    def test_get_recipient_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_recipient_detail_url)
        
    def test_get_recipient_not_auth(self):
        self._test_get_detail_not_auth(self._hook_recipient_detail_url())
        
    def test_get_recipient_not_found(self):
        self._test_get_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id))       
        
    def test_put_recipient_ok(self):
        data = {'chat_id': 'abdc', 'name': 'new_name', 'username': 'new_username'} 
        self._test_put_detail_ok(self._hook_recipient_detail_url(), data, KikRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        updated = KikRecipient.objects.get(pk=self.recipient.pk)
        self.assertEqual(updated.name, 'new_name')
        self.assertEqual(updated.chat_id, 'abdc')
        self.assertEqual(updated.username, 'new_username')
        self.assertRecipient(data['chat_id'], data['name'], data['username'], updated)
        
    def test_put_recipient_from_other_bot(self):
        data = {'chat_id': 'abdc', 'name': 'new_name', 'username': 'new_username'}
        self._test_put_detail_from_other_bot(self._hook_recipient_detail_url, data, KikRecipientDetail, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_auth(self):
        data = {'chat_id': 'abdc', 'name': 'new_name', 'username': 'new_username'}
        self._test_put_detail_not_auth(self._hook_recipient_detail_url(), data, KikRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_found(self):
        data = {'chat_id': 'abdc', 'name': 'new_name', 'username': 'new_username'}
        self._test_put_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), data, 
                                        KikRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)

    def test_delete_recipient_ok(self):
        self._test_delete_detail_ok(self._hook_recipient_detail_url(), KikRecipientDetail, 
                                    self.bot.pk, self.hook.pk, self.hook.kik_recipients.all()[0].pk)
        
    def test_delete_recipient_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_recipient_detail_url, KikRecipientDetail, 
                                                self.bot.pk, self.hook.pk, self.hook.kik_recipients.all()[0].pk)
        
    def test_delete_recipient_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_recipient_detail_url(), KikRecipientDetail, 
                                          self.bot.pk, self.hook.pk, self.hook.kik_recipients.all()[0].pk)
        
    def test_delete_recipient_not_found(self):
        self._test_delete_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), 
                                           KikRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)
        
class TestHookMessengerRecipientAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHookMessengerRecipientAPI, self).setUp()
        self.hook = factories.HookFactory(bot=self.bot)
        self.recipient = factories.MessengerRecipientFactory(hook=self.hook)
        
    def _hook_recipient_list_url(self, bot_pk=None, hook_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        return '%s/bots/%s/hooks/%s/recipients/messenger/' % (self.api, bot_pk, hook_pk)
    
    def _hook_recipient_detail_url(self, bot_pk=None, hook_pk=None, recipient_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not hook_pk:
            hook_pk = self.hook.pk
        if not recipient_pk:
            recipient_pk = self.hook.messenger_recipients.all()[0].pk
        return '%s/bots/%s/hooks/%s/recipients/messenger/%s/' % (self.api, bot_pk, hook_pk, recipient_pk)
    
    def assertRecipient(self, chat_id, name, recipient=None):
        if not recipient:
            recipient = self.hook.messenger_recipients.all()[0]
        self.assertEqual(recipient.chat_id, chat_id)
        self.assertEqual(recipient.name, name)

    def test_get_hook_recipients_ok(self):
        data = self._test_get_list_ok(self._hook_recipient_list_url())
        self.assertRecipient(data[0]['chat_id'], data[0]['name'])
        
    def test_get_hook_recipients_not_auth(self):
        self._test_get_list_not_auth(self._hook_recipient_list_url())
        
    def test_post_hook_recipient_ok(self):
        data = {'chat_id': self.hook.messenger_recipients.all()[0].chat_id, 'name': self.hook.messenger_recipients.all()[0].name, }                              
        data = self._test_post_list_ok(self._hook_recipient_list_url(), MessengerRecipient, data)
        new_recipient = MessengerRecipient.objects.filter(hook=self.hook)[0]        
        self.assertRecipient(self.hook.messenger_recipients.all()[0].chat_id, self.hook.messenger_recipients.all()[0].name, 
                             recipient=new_recipient)
        self.assertRecipient(data['chat_id'], data['name'], new_recipient)
        
    def test_post_hook_recipient_not_auth(self):
        data = {'chat_id': self.hook.messenger_recipients.all()[0].chat_id, 'name': self.hook.messenger_recipients.all()[0].name, }
        self._test_post_list_not_auth(self._hook_recipient_list_url(), data)
        
    def test_get_recipient_ok(self):
        data = self._test_get_detail_ok(self._hook_recipient_detail_url())
        self.assertRecipient(data['chat_id'], data['name'])
        
    def test_get_recipient_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._hook_recipient_detail_url)
        
    def test_get_recipient_not_auth(self):
        self._test_get_detail_not_auth(self._hook_recipient_detail_url())
        
    def test_get_recipient_not_found(self):
        self._test_get_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id))       
        
    def test_put_recipient_ok(self):
        data = {'chat_id': 'abdc', 'name': 'new_name'} 
        self._test_put_detail_ok(self._hook_recipient_detail_url(), data, MessengerRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        updated = MessengerRecipient.objects.get(pk=self.recipient.pk)
        self.assertEqual(updated.name, 'new_name')
        self.assertEqual(updated.chat_id, 'abdc')
        self.assertRecipient(data['chat_id'], data['name'], updated)
        
    def test_put_recipient_from_other_bot(self):
        data = {'chat_id': 'abdc', 'name': 'new_name'}
        self._test_put_detail_from_other_bot(self._hook_recipient_detail_url, data, MessengerRecipientDetail, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_auth(self):
        data = {'chat_id': 'abdc', 'name': 'new_name'}
        self._test_put_detail_not_auth(self._hook_recipient_detail_url(), data, MessengerRecipientDetail, self.bot.pk, self.hook.pk, self.recipient.pk)
        
    def test_put_recipient_not_found(self):
        data = {'chat_id': 'abdc', 'name': 'new_name'}
        self._test_put_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), data, 
                                        MessengerRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)

    def test_delete_recipient_ok(self):
        self._test_delete_detail_ok(self._hook_recipient_detail_url(), MessengerRecipientDetail, 
                                    self.bot.pk, self.hook.pk, self.hook.messenger_recipients.all()[0].pk)
        
    def test_delete_recipient_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._hook_recipient_detail_url, MessengerRecipientDetail, 
                                                self.bot.pk, self.hook.pk, self.hook.messenger_recipients.all()[0].pk)
        
    def test_delete_recipient_not_auth(self):
        self._test_delete_detail_not_auth(self._hook_recipient_detail_url(), MessengerRecipientDetail, 
                                          self.bot.pk, self.hook.pk, self.hook.messenger_recipients.all()[0].pk)
        
    def test_delete_recipient_not_found(self):
        self._test_delete_detail_not_found(self._hook_recipient_detail_url(recipient_pk=self.unlikely_id), 
                                           MessengerRecipientDetail, self.bot.pk, self.hook.pk, self.unlikely_id)
