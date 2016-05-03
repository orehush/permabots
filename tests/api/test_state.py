#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import State, TelegramChatState, KikChatState, MessengerChatState
from microbot.test import factories
from microbot.views import StateDetail, TelegramChatStateDetail, KikChatStateDetail, MessengerChatStateDetail
from tests.api.base import BaseTestAPI

class TestStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        
    def _state_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/states/' % (self.api, bot_pk)
    
    def _state_detail_url(self, bot_pk=None, state_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not state_pk:
            state_pk = self.state.pk
        return '%s/bots/%s/states/%s/' % (self.api, bot_pk, state_pk)
    
    def assertState(self, id, created_at, updated_at, name, state=None):
        if not state:
            state = self.state
        self.assertEqual(state.name, name)
        self.assertMicrobotModel(id, created_at, updated_at, state)
        
    def test_get_states_ok(self):
        data = self._test_get_list_ok(self._state_list_url())
        self.assertState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'])
        
    def test_get_states_not_auth(self):
        self._test_get_list_not_auth(self._state_list_url())
        
    def test_post_states_ok(self):
        data = self._test_post_list_ok(self._state_list_url(), State, {'name': self.state.name})
        new_state = State.objects.filter(bot=self.bot)[0]
        self.assertState(None, self.state.created_at, self.state.updated_at, self.state.name, new_state)
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'], new_state)
        
    def test_post_states_not_auth(self):
        self._test_post_list_not_auth(self._state_list_url(), {'name': self.state.name})
                
    def test_get_state_ok(self):
        data = self._test_get_detail_ok(self._state_detail_url())
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'])
        
    def test_get_state_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._state_detail_url)
        
    def test_get_state_not_auth(self):
        self._test_get_detail_not_auth(self._state_detail_url())
        
    def test_get_state_var_not_found(self):
        self._test_get_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id))
        
    def test_put_state_ok(self):
        data = self._test_put_detail_ok(self._state_detail_url(), {'name': 'new_value'}, StateDetail, self.bot.pk, self.state.pk)
        updated = State.objects.get(pk=self.state.pk)
        self.assertEqual(updated.name, 'new_value')
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'], updated)

    def test_put_state_from_other_bot(self):
        self._test_put_detail_from_other_bot(self._state_detail_url, {'name': 'new_value'}, StateDetail, self.state.pk)
        
    def test_put_state_not_auth(self):
        self._test_put_detail_not_auth(self._state_detail_url(), {'name': 'new_value'}, StateDetail,
                                       self.bot.pk, self.state.pk)
        
    def test_put_state_not_found(self):
        self._test_put_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id), {'name': 'new_value'}, StateDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_state_ok(self):
        self._test_delete_detail_ok(self._state_detail_url(), StateDetail, self.bot.pk, self.state.pk)
        self.assertEqual(State.objects.count(), 0)
        
    def test_delete_state_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._state_detail_url, StateDetail, self.state.pk)
        
    def test_delete_state_not_auth(self):
        self._test_delete_detail_not_auth(self._state_detail_url(), StateDetail, self.bot.pk, self.state.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._state_detail_url(state_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)
        
        
class TestTelegramChatStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestTelegramChatStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        self.user = factories.TelegramUserAPIFactory(id=self.telegram_update.message.from_user.id,
                                                     username=self.telegram_update.message.from_user.username,
                                                     first_name=self.telegram_update.message.from_user.first_name,
                                                     last_name=self.telegram_update.message.from_user.last_name)
        self.chat = factories.TelegramChatAPIFactory(id=self.telegram_update.message.chat.id,
                                                     type=self.telegram_update.message.chat.type, 
                                                     title=self.telegram_update.message.chat.title,
                                                     username=self.telegram_update.message.chat.username,
                                                     first_name=self.telegram_update.message.chat.first_name,
                                                     last_name=self.telegram_update.message.chat.last_name)
        self.chatstate = factories.TelegramChatStateFactory(state=self.state,
                                                            chat=self.chat,
                                                            user=self.user)
        
    def _chatstate_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/chatstates/telegram/' % (self.api, bot_pk)
    
    def _chatstate_detail_url(self, bot_pk=None, chatstate_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not chatstate_pk:
            chatstate_pk = self.chatstate.pk
        return '%s/bots/%s/chatstates/telegram/%s/' % (self.api, bot_pk, chatstate_pk)
    
    def assertTelegramChatState(self, id, created_at, updated_at, name, chat_id, user_id, chatstate=None):
        if not chatstate:
            chatstate = self.chatstate
        self.assertEqual(chatstate.state.name, name)
        self.assertEqual(chatstate.chat.id, chat_id)
        self.assertEqual(chatstate.user.id, user_id)
        self.assertMicrobotModel(id, created_at, updated_at, chatstate)
        
    def test_get_chatstates_ok(self):
        data = self._test_get_list_ok(self._chatstate_list_url())
        self.assertTelegramChatState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['state']['name'], data[0]['chat'], data[0]['user'])
        
    def test_get_chatstates_not_auth(self):
        self._test_get_list_not_auth(self._chatstate_list_url())
        
    def test_post_chatstates_ok(self):
        data = self._test_post_list_ok(self._chatstate_list_url(), TelegramChatState, 
                                       {'chat': self.chat.id, 'user': self.user.id, 
                                        'state': {'name': self.state.name}})
        new_chatstate = TelegramChatState.objects.filter(state=self.state)[0]
        self.assertTelegramChatState(None, self.chatstate.created_at, self.chatstate.updated_at, 
                                     self.chatstate.state.name, self.chatstate.chat.id, self.chatstate.user.id, new_chatstate)
        self.assertTelegramChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'], new_chatstate)

    def test_post_chatstates_new_state_not_found(self):
        self._test_post_list_not_found_required_pre_created(self._chatstate_list_url(), TelegramChatState, 
                                                            {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': 'joolo'}})
        
    def test_post_chatstates_not_auth(self):
        self._test_post_list_not_auth(self._chatstate_list_url(), {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': self.state.name}})
                
    def test_get_chatstate_ok(self):
        data = self._test_get_detail_ok(self._chatstate_detail_url())
        self.assertTelegramChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'])
        
    def test_get_chatstate_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._chatstate_detail_url)
        
    def test_get_chatstate_not_auth(self):
        self._test_get_detail_not_auth(self._chatstate_detail_url())
        
    def test_get_chatstate_var_not_found(self):
        self._test_get_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id))
        
    def test_put_chatstate_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        data = self._test_put_detail_ok(self._chatstate_detail_url(), 
                                        {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': new_state.name}}, 
                                        TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
        updated = TelegramChatState.objects.get(pk=self.chatstate.pk)
        self.assertEqual(updated.state.name, new_state.name)
        self.assertTelegramChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'], updated)
 
    def test_put_chatstate_only_state_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'state': {'name': new_state.name}}, 
                                 TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(TelegramChatState.objects.get(pk=self.chatstate.pk).state.name, new_state.name)
        
    def test_put_chatstate_only_chat_ok(self):
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'chat': self.chat.id}, 
                                 TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(TelegramChatState.objects.get(pk=self.chatstate.pk).state.name, self.chatstate.state.name)
        
    def test_put_chatstate_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_from_other_bot(self._chatstate_detail_url, 
                                             {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': new_state.name}}, 
                                             TelegramChatStateDetail, self.chatstate.pk)
        
    def test_put_chatstate_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_auth(self._chatstate_detail_url(), {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': new_state.name}}, 
                                       TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
        
    def test_put_chatstate_not_found(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), 
                                        {'chat': self.chat.id, 'user': self.user.id, 'state': {'name': new_state.name}}, TelegramChatStateDetail, 
                                        self.bot.pk, self.unlikely_id)
          
    def test_delete_chatstate_ok(self):
        self._test_delete_detail_ok(self._chatstate_detail_url(), TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(TelegramChatState.objects.count(), 0)
        
    def test_delete_chatstate_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._chatstate_detail_url, TelegramChatStateDetail, self.chatstate.pk)
        
    def test_delete_chatstate_not_auth(self):
        self._test_delete_detail_not_auth(self._chatstate_detail_url(), TelegramChatStateDetail, self.bot.pk, self.chatstate.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)
        
class TestKikChatStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestKikChatStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        self.user = factories.KikUserAPIFactory(username=self.kik_message.from_user)
        self.chat = factories.KikChatAPIFactory(id=self.kik_message.chat_id)
        self.chatstate = factories.KikChatStateFactory(state=self.state,
                                                       chat=self.chat,
                                                       user=self.user)
        
    def _chatstate_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/chatstates/kik/' % (self.api, bot_pk)
    
    def _chatstate_detail_url(self, bot_pk=None, chatstate_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not chatstate_pk:
            chatstate_pk = self.chatstate.pk
        return '%s/bots/%s/chatstates/kik/%s/' % (self.api, bot_pk, chatstate_pk)
    
    def assertKikChatState(self, id, created_at, updated_at, name, chat_id, user_id, chatstate=None):
        if not chatstate:
            chatstate = self.chatstate
        self.assertEqual(chatstate.state.name, name)
        self.assertEqual(chatstate.chat.id, chat_id)
        self.assertEqual(chatstate.user.username, user_id)
        self.assertMicrobotModel(id, created_at, updated_at, chatstate)
        
    def test_get_chatstates_ok(self):
        data = self._test_get_list_ok(self._chatstate_list_url())
        self.assertKikChatState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['state']['name'], data[0]['chat'], data[0]['user'])
        
    def test_get_chatstates_not_auth(self):
        self._test_get_list_not_auth(self._chatstate_list_url())
        
    def test_post_chatstates_ok(self):
        data = self._test_post_list_ok(self._chatstate_list_url(), KikChatState, 
                                       {'chat': self.chat.id, 'user': self.user.username, 
                                        'state': {'name': self.state.name}})
        new_chatstate = KikChatState.objects.filter(state=self.state)[0]
        self.assertKikChatState(None, self.chatstate.created_at, self.chatstate.updated_at, 
                                self.chatstate.state.name, self.chatstate.chat.id, self.chatstate.user.username, new_chatstate)
        self.assertKikChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'], new_chatstate)

    def test_post_chatstates_new_state_not_found(self):
        self._test_post_list_not_found_required_pre_created(self._chatstate_list_url(), KikChatState, 
                                                            {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': 'joolo'}})
        
    def test_post_chatstates_not_auth(self):
        self._test_post_list_not_auth(self._chatstate_list_url(), {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': self.state.name}})
                
    def test_get_chatstate_ok(self):
        data = self._test_get_detail_ok(self._chatstate_detail_url())
        self.assertKikChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'])
        
    def test_get_chatstate_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._chatstate_detail_url)
        
    def test_get_chatstate_not_auth(self):
        self._test_get_detail_not_auth(self._chatstate_detail_url())
        
    def test_get_chatstate_var_not_found(self):
        self._test_get_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id))
        
    def test_put_chatstate_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        data = self._test_put_detail_ok(self._chatstate_detail_url(), 
                                        {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': new_state.name}}, 
                                        KikChatStateDetail, self.bot.pk, self.chatstate.pk)
        updated = KikChatState.objects.get(pk=self.chatstate.pk)
        self.assertEqual(updated.state.name, new_state.name)
        self.assertKikChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], data['user'], updated)
 
    def test_put_chatstate_only_state_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'state': {'name': new_state.name}}, 
                                 KikChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(KikChatState.objects.get(pk=self.chatstate.pk).state.name, new_state.name)
        
    def test_put_chatstate_only_chat_ok(self):
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'chat': self.chat.id}, 
                                 KikChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(KikChatState.objects.get(pk=self.chatstate.pk).state.name, self.chatstate.state.name)
        
    def test_put_chatstate_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_from_other_bot(self._chatstate_detail_url, 
                                             {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': new_state.name}}, 
                                             KikChatStateDetail, self.chatstate.pk)
        
    def test_put_chatstate_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_auth(self._chatstate_detail_url(), {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': new_state.name}}, 
                                       KikChatStateDetail, self.bot.pk, self.chatstate.pk)
        
    def test_put_chatstate_not_found(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), 
                                        {'chat': self.chat.id, 'user': self.user.username, 'state': {'name': new_state.name}}, KikChatStateDetail, 
                                        self.bot.pk, self.unlikely_id)
          
    def test_delete_chatstate_ok(self):
        self._test_delete_detail_ok(self._chatstate_detail_url(), KikChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(KikChatState.objects.count(), 0)
        
    def test_delete_chatstate_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._chatstate_detail_url, KikChatStateDetail, self.chatstate.pk)
        
    def test_delete_chatstate_not_auth(self):
        self._test_delete_detail_not_auth(self._chatstate_detail_url(), KikChatStateDetail, self.bot.pk, self.chatstate.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)
        
class TestMessengerChatStateAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestMessengerChatStateAPI, self).setUp()
        self.state = factories.StateFactory(bot=self.bot)
        self.chat = self.messenger_text_message.sender
        self.chatstate = factories.MessengerChatStateFactory(state=self.state,
                                                             chat=self.chat)
        
    def _chatstate_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/chatstates/messenger/' % (self.api, bot_pk)
    
    def _chatstate_detail_url(self, bot_pk=None, chatstate_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not chatstate_pk:
            chatstate_pk = self.chatstate.pk
        return '%s/bots/%s/chatstates/messenger/%s/' % (self.api, bot_pk, chatstate_pk)
    
    def assertMessengerChatState(self, id, created_at, updated_at, name, chat_id, chatstate=None):
        if not chatstate:
            chatstate = self.chatstate
        self.assertEqual(chatstate.state.name, name)
        self.assertEqual(chatstate.chat, chat_id)
        self.assertMicrobotModel(id, created_at, updated_at, chatstate)
        
    def test_get_chatstates_ok(self):
        data = self._test_get_list_ok(self._chatstate_list_url())
        self.assertMessengerChatState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['state']['name'], data[0]['chat'])
        
    def test_get_chatstates_not_auth(self):
        self._test_get_list_not_auth(self._chatstate_list_url())
        
    def test_post_chatstates_ok(self):
        data = self._test_post_list_ok(self._chatstate_list_url(), MessengerChatState, 
                                       {'chat': self.chat,  
                                        'state': {'name': self.state.name}})
        new_chatstate = MessengerChatState.objects.filter(state=self.state)[0]
        self.assertMessengerChatState(None, self.chatstate.created_at, self.chatstate.updated_at, 
                                      self.chatstate.state.name, self.chatstate.chat, new_chatstate)
        self.assertMessengerChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], new_chatstate)

    def test_post_chatstates_new_state_not_found(self):
        self._test_post_list_not_found_required_pre_created(self._chatstate_list_url(), MessengerChatState, 
                                                            {'chat': self.chat, 'state': {'name': 'joolo'}})
        
    def test_post_chatstates_not_auth(self):
        self._test_post_list_not_auth(self._chatstate_list_url(), {'chat': self.chat, 'state': {'name': self.state.name}})
                
    def test_get_chatstate_ok(self):
        data = self._test_get_detail_ok(self._chatstate_detail_url())
        self.assertMessengerChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'])
        
    def test_get_chatstate_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._chatstate_detail_url)
        
    def test_get_chatstate_not_auth(self):
        self._test_get_detail_not_auth(self._chatstate_detail_url())
        
    def test_get_chatstate_var_not_found(self):
        self._test_get_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id))
        
    def test_put_chatstate_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        data = self._test_put_detail_ok(self._chatstate_detail_url(), 
                                        {'chat': self.chat, 'state': {'name': new_state.name}}, 
                                        MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
        updated = MessengerChatState.objects.get(pk=self.chatstate.pk)
        self.assertEqual(updated.state.name, new_state.name)
        self.assertMessengerChatState(data['id'], data['created_at'], data['updated_at'], data['state']['name'], data['chat'], updated)
 
    def test_put_chatstate_only_state_ok(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'state': {'name': new_state.name}}, 
                                 MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(MessengerChatState.objects.get(pk=self.chatstate.pk).state.name, new_state.name)
        
    def test_put_chatstate_only_chat_ok(self):
        self._test_put_detail_ok(self._chatstate_detail_url(), 
                                 {'chat': self.chat}, 
                                 MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(MessengerChatState.objects.get(pk=self.chatstate.pk).state.name, self.chatstate.state.name)
        
    def test_put_chatstate_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_from_other_bot(self._chatstate_detail_url, 
                                             {'chat': self.chat, 'state': {'name': new_state.name}}, 
                                             MessengerChatStateDetail, self.chatstate.pk)
        
    def test_put_chatstate_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_auth(self._chatstate_detail_url(), {'chat': self.chat, 'state': {'name': new_state.name}}, 
                                       MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
        
    def test_put_chatstate_not_found(self):
        new_state = factories.StateFactory(bot=self.bot)
        self._test_put_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), 
                                        {'chat': self.chat, 'state': {'name': new_state.name}}, MessengerChatStateDetail, 
                                        self.bot.pk, self.unlikely_id)
          
    def test_delete_chatstate_ok(self):
        self._test_delete_detail_ok(self._chatstate_detail_url(), MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
        self.assertEqual(MessengerChatState.objects.count(), 0)
        
    def test_delete_chatstate_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._chatstate_detail_url, MessengerChatStateDetail, self.chatstate.pk)
        
    def test_delete_chatstate_not_auth(self):
        self._test_delete_detail_not_auth(self._chatstate_detail_url(), MessengerChatStateDetail, self.bot.pk, self.chatstate.pk)
       
    def test_delete_state_not_found(self):
        self._test_delete_detail_not_found(self._chatstate_detail_url(chatstate_pk=self.unlikely_id), StateDetail, self.bot.pk, self.unlikely_id)                