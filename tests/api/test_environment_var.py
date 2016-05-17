#!/usr/bin/env python
# -*- coding: utf-8 -*-
from permabots.models import EnvironmentVar
from permabots.views import EnvironmentVarDetail
from tests.api.base import BaseTestAPI

class TestEnvironmentVarAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestEnvironmentVarAPI, self).setUp()
        self.key = "shop"
        self.value = "myebookshop"
        self.env_var = EnvironmentVar.objects.create(bot=self.bot,
                                                     key=self.key, 
                                                     value=self.value)
        
    def _env_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/env/' % (self.api, bot_pk)
    
    def _env_detail_url(self, bot_pk=None, env_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not env_pk:
            env_pk = self.env_var.pk
        return '%s/bots/%s/env/%s/' % (self.api, bot_pk, env_pk)
    
    def assertEnvVar(self, id, created_at, updated_at, key, value, env_var=None):
        if not env_var:
            env_var = self.env_var
        self.assertEqual(env_var.key, key)
        self.assertEqual(env_var.value, value)
        self.assertPermabotsModel(id, created_at, updated_at, env_var)
        
    def test_get_env_vars_ok(self):
        data = self._test_get_list_ok(self._env_list_url())
        self.assertEnvVar(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value'])
        
    def test_get_env_vars_not_auth(self):
        self._test_get_list_not_auth(self._env_list_url())
        
    def test_post_env_vars_ok(self):
        data = self._test_post_list_ok(self._env_list_url(), EnvironmentVar, {'key': self.key, 'value': self.value})
        new_env_var = EnvironmentVar.objects.filter(bot=self.bot)[0]
        self.assertEnvVar(None, self.env_var.created_at, self.env_var.updated_at, self.key, self.value, new_env_var)
        self.assertEnvVar(data['id'], data['created_at'], data['updated_at'], data['key'], data['value'], new_env_var)
        
    def test_post_env_vars_not_auth(self):
        self._test_post_list_not_auth(self._env_list_url(), {'key': self.key, 'value': self.value})
                
    def test_get_env_var_ok(self):
        data = self._test_get_detail_ok(self._env_detail_url())
        self.assertEnvVar(data['id'], data['created_at'], data['updated_at'], data['key'], data['value'])
        
    def test_get_env_var_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._env_detail_url)
        
    def test_get_env_var_not_auth(self):
        self._test_get_detail_not_auth(self._env_detail_url())
        
    def test_get_env_var_not_found(self):
        self._test_get_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id))
        
    def test_put_env_var_ok(self):
        data = self._test_put_detail_ok(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        updated = EnvironmentVar.objects.get(pk=self.env_var.pk)
        self.assertEqual(updated.value, 'new_value')
        self.assertEnvVar(data['id'], data['created_at'], data['updated_at'], data['key'], data['value'], updated)
        
    def test_put_env_var_from_other_bot(self):
        self._test_put_detail_from_other_bot(self._env_detail_url, {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail, self.env_var.pk)
        
    def test_put_env_var_not_auth(self):
        self._test_put_detail_not_auth(self._env_detail_url(), {'key': self.key, 'value': 'new_value'}, EnvironmentVarDetail,
                                       self.bot.pk, self.env_var.pk)
        
    def test_put_env_var_not_found(self):
        self._test_put_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id), {'key': self.key, 'value': 'new_value'}, 
                                        EnvironmentVarDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_env_var_ok(self):
        self._test_delete_detail_ok(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
        self.assertEqual(EnvironmentVar.objects.count(), 0)
        
    def test_delete_env_var_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._env_detail_url, EnvironmentVarDetail, self.env_var.pk)
        
    def test_delete_env_var_not_auth(self):
        self._test_delete_detail_not_auth(self._env_detail_url(), EnvironmentVarDetail, self.bot.pk, self.env_var.pk)
       
    def test_delete_env_var_not_found(self):
        self._test_delete_detail_not_found(self._env_detail_url(env_pk=self.unlikely_id), EnvironmentVarDetail, self.bot.pk, self.unlikely_id)