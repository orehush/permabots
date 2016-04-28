#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Handler, State
from microbot.test import factories
from microbot.views import HandlerDetail, UrlParameterDetail, HeaderParameterDetail, SourceStateDetail
from microbot.models.handler import HeaderParam, UrlParam, Request
from tests.api.base import BaseTestAPI

class TestHandlerAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.url_param = factories.UrlParamFactory(request=self.handler.request)
        self.header_param = factories.HeaderParamFactory(request=self.handler.request)
        
    def _handler_list_url(self, bot_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        return '%s/bots/%s/handlers/' % (self.api, bot_pk)
    
    def _handler_detail_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/' % (self.api, bot_pk, handler_pk)
    
    def _handler_url_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/urlparams/' % (self.api, bot_pk, handler_pk)    
    
    def _handler_header_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/headerparams/' % (self.api, bot_pk, handler_pk)            
    
    def assertHandler(self, id, created_at, updated_at, name, pattern, response_text_template, response_keyboard_template, enabled, priority, target_state_name, 
                      url_template, method, data, source_states_names, handler=None):
        if not handler:
            handler = self.handler
        self.assertEqual(handler.name, name)
        self.assertEqual(handler.pattern, pattern)
        self.assertEqual(handler.response.text_template, response_text_template)
        self.assertEqual(handler.response.keyboard_template, response_keyboard_template)
        if handler.request:
            self.assertEqual(handler.request.url_template, url_template)
            self.assertEqual(handler.request.method, method)
            self.assertEqual(handler.request.data, data)
        self.assertEqual(handler.enabled, enabled)
        self.assertEqual(handler.priority, priority)
        self.assertMicrobotModel(id, created_at, updated_at, handler)
        if handler.target_state or target_state_name:
            self.assertEqual(handler.target_state.name, target_state_name)
        if handler.source_states.count() > 0 or source_states_names:
            self.assertEqual(handler.source_states.count(), len(source_states_names))
            for source_state_name in source_states_names:
                handler.source_states.get(name=source_state_name)            
        
    def assertUrlParam(self, key, value_template, url_param=None):
        if not url_param:
            url_param = self.url_param
        self.assertEqual(url_param.key, key)
        self.assertEqual(url_param.value_template, value_template)

    def assertHeaderParam(self, key, value_template, header_param=None):
        if not header_param:
            header_param = self.header_param
        self.assertEqual(header_param.key, key)
        self.assertEqual(header_param.value_template, value_template)
        
    def test_get_handlers_ok(self):
        data = self._test_get_list_ok(self._handler_list_url())
        self.assertHandler(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                           data[0]['pattern'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                           data[0]['enabled'], data[0]['priority'], None, data[0]['request']['url_template'], 
                           data[0]['request']['method'], data[0]['request']['data'], None)
        
    def test_get_handlers_with_source_states_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.source_states.add(self.state)
        data = self._test_get_list_ok(self._handler_list_url())
        self.assertHandler(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'], 
                           data[0]['pattern'], data[0]['response']['text_template'], data[0]['response']['keyboard_template'],
                           data[0]['enabled'], data[0]['priority'], None, data[0]['request']['url_template'],
                           data[0]['request']['method'], data[0]['request']['data'], [self.state.name])
        
    def test_get_handlers_not_auth(self):
        self._test_get_list_not_auth(self._handler_list_url())
        
    def test_post_handlers_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern,
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False, 'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                              'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                  'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                              'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                     'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                              }                                                                         
                }
        data = self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, None, self.handler.request.url_template, self.handler.request.method, 
                           self.handler.request.data, None, new_handler)
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], 
                           data['pattern'], data['response']['text_template'], data['response']['keyboard_template'],
                           data['enabled'], data['priority'], None, data['request']['url_template'], 
                           data['request']['method'], data['request']['data'], None, new_handler)
    
    def test_post_handler_validation_error(self):
        data = {'name': self.handler.name, 'pattern': '(?P<pk>%i', 
                'request': {'url_template': '{{a', 'method': self.handler.request.method,
                                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                   'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                            },
                'response': {'text_template': '<i>{{a',
                             'keyboard_template': '[["{{","asdasd"]'},
                'enabled': False,                                                                        
                }
        errors = self._test_post_list_validation_error(self._handler_list_url(), Handler, data)
        self.assertNotEqual(None, errors['pattern'][0])
        self.assertNotEqual(None, errors['request']['url_template'][0])
        self.assertNotEqual(None, errors['response']['text_template'][0])
        self.assertNotEqual(None, errors['response']['text_template'][1])
        self.assertNotEqual(None, errors['response']['keyboard_template'][0])
    
    def test_post_handlers_with_no_request_ok(self):
        self.handler.request = None
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False                                                                         
                }
        self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, None, None, None,
                           None, None, new_handler)
        
    def test_post_handlers_with_target_state_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'target_state': {'name': self.state.name}, 'priority': self.handler.priority,
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False, 'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                              'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                  'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                              'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                     'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                              }                                                                         
                }
        self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, self.handler.target_state.name, 
                           self.handler.request.url_template, self.handler.request.method, 
                           self.handler.request.data, None, new_handler)
        self.assertEqual(self.handler.target_state, new_handler.target_state)
        
    def test_post_handlers_with_target_state_new_state_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 
                'target_state': {'name': 'new_state'}, 'priority': self.handler.priority,
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False, 'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                              'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                  'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                              'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                     'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                              }                                                                         
                }
        self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, new_handler.target_state.name, self.handler.request.url_template,
                           self.handler.request.method, self.handler.request.data, None, new_handler)
        
    def test_post_handlers_with_request_data(self):
        self.handler.request.method = Request.POST
        self.handler.request.data = "{'one': 'two'}"
        self.handler.request.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern,
                'response': {'text_template': self.handler.response.text_template,
                             'keyboard_template': self.handler.response.keyboard_template},
                'enabled': False, 'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                                              'data': self.handler.request.data,
                                              'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                                  'value_template': self.handler.request.url_parameters.all()[0].value_template}],
                                              'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                                     'value_template': self.handler.request.header_parameters.all()[0].value_template}]
                                              }                                                                         
                }
        data = self._test_post_list_ok(self._handler_list_url(), Handler, data)
        new_handler = Handler.objects.filter(bot=self.bot)[0]
        self.assertHandler(None, self.handler.created_at, self.handler.updated_at, self.handler.name, self.handler.pattern, 
                           self.handler.response.text_template, self.handler.response.keyboard_template,
                           False, self.handler.priority, None, self.handler.request.url_template, self.handler.request.method, 
                           self.handler.request.data, None, new_handler)
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], 
                           data['pattern'], data['response']['text_template'], data['response']['keyboard_template'],
                           data['enabled'], data['priority'], None, data['request']['url_template'], 
                           data['request']['method'], data['request']['data'], None, new_handler)
        
    def test_post_handlers_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': self.handler.request}
        self._test_post_list_not_auth(self._handler_list_url(), data)
        
    def test_get_handler_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = self._test_get_detail_ok(self._handler_detail_url())
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], data['pattern'], 
                           data['response']['text_template'], data['response']['keyboard_template'], 
                           data['enabled'], data['priority'], data['target_state']['name'], 
                           data['request']['url_template'], data['request']['method'], data['request']['data'], None)
        
    def test_get_handler_with_source_states_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.source_states.add(self.state)
        data = self._test_get_detail_ok(self._handler_detail_url())
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], data['pattern'], 
                           data['response']['text_template'], data['response']['keyboard_template'], 
                           data['enabled'], data['priority'], None, data['request']['url_template'], 
                           data['request']['method'], data['request']['data'], [data['source_states'][0]['name']])

    def test_get_handler_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_detail_url)
        
    def test_get_handler_not_auth(self):
        self._test_get_detail_not_auth(self._handler_detail_url())
        
    def test_get_handler_not_found(self):
        self._test_get_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id))
        
    def test_put_handler_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': -1,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            }
                }
        data = self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        updated = Handler.objects.get(pk=self.handler.pk)
        self.assertEqual(updated.enabled, False)
        self.assertEqual(updated.priority, -1)
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        self.assertHandler(data['id'], data['created_at'], data['updated_at'], data['name'], 
                           data['pattern'], data['response']['text_template'], data['response']['keyboard_template'],
                           data['enabled'], data['priority'], None, data['request']['url_template'], 
                           data['request']['method'], data['request']['data'], None, updated)

    def test_put_handler_only_name_ok(self):
        data = {'name': 'new_name'}
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).name, 'new_name')
        
    def test_put_handler_only_pattern_ok(self):
        data = {'pattern': 'new_pattern'}
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).pattern, 'new_pattern')
        
    def test_put_handler_only_pattern_validation_error(self):
        data = {'pattern': '(?P<pk>%i'}
        response = self._test_put_detail_validation_error(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertNotEqual(None, response.data['pattern'][0])

    def test_put_handler_only_priority_ok(self):
        data = {'priority': 7}
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).priority, 7)
        
    def test_put_handler_only_response_keyboard_ok(self):
        keyboard = "[['{{asdasas}}']]"
        data = {'response': {'keyboard_template': keyboard}}
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).response.keyboard_template, keyboard)    
        
    def test_put_handler_only_response_validation_error(self):
        keyboard = '["{{asdasd"]]'
        data = {'response': {'text_template': '<em>{{a',
                             'keyboard_template': keyboard}}
        response = self._test_put_detail_validation_error(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertIn('Jinja error', response.data['response']['text_template'][0])
        self.assertIn('Not correct', response.data['response']['text_template'][1])
        self.assertIn('Jinja error', response.data['response']['keyboard_template'][0])
        
    def test_put_handler_only_request_url_template_ok(self):
        url_template = '/github{{env.token}}'
        data = {'request': {'url_template': url_template}}
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).request.url_template, url_template)
        
    def test_put_handler_only_request_url_template_validatin_error(self):
        url_template = '/github{{env.token}'
        data = {'request': {'url_template': url_template}}
        response = self._test_put_detail_validation_error(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertNotEqual(None, response.data['request']['url_template'][0])

    def test_put_handler_no_request_ok(self):
        self.handler.request = None
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).request, None)

    def test_put_handler_with_target_new_state_ok(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,                                                                                 
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            },
                'target_state': {'name': 'new_state'}, 
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).target_state.name, 'new_state')
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_with_target_state_ok(self):
        self.state = factories.StateFactory(bot=self.bot)
        self.handler.target_state = self.state
        self.handler.save()
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,                                                                                 
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': 2,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'url_parameters': [{'key': self.handler.request.url_parameters.all()[0].key,
                                                'value_template': 'new_url_param_value'}],
                            'header_parameters': [{'key': self.handler.request.header_parameters.all()[0].key,
                                                   'value_template': 'new_header_param_value'}]
                            },
                'target_state': {'name': self.state.name}, 
                }
        self._test_put_detail_ok(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).enabled, False)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).priority, 2)
        self.assertEqual(Handler.objects.get(pk=self.handler.pk).target_state, self.state)
        self.assertEqual(UrlParam.objects.get(key=self.handler.request.url_parameters.all()[0].key).value_template, 'new_url_param_value')
        self.assertEqual(HeaderParam.objects.get(key=self.handler.request.header_parameters.all()[0].key).value_template, 'new_header_param_value')
        
    def test_put_handler_from_other_bot(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_from_other_bot(self._handler_detail_url, data, HandlerDetail, self.handler.pk)
        
    def test_put_handler_not_auth(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_auth(self._handler_detail_url(), data, HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_put_handler_not_found(self):
        data = {'name': self.handler.name, 'pattern': self.handler.pattern, 'response': {'text_template': self.handler.response.text_template,
                'keyboard_template': self.handler.response.keyboard_template}, 'enabled': False, 'priority': self.handler.priority,
                'request': {'url_template': self.handler.request.url_template, 'method': self.handler.request.method,
                            'data': self.handler.request.data}
                }
        self._test_put_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id), data, HandlerDetail, self.bot.pk, self.unlikely_id)
          
    def test_delete_handler_ok(self):
        self._test_delete_detail_ok(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        self.assertEqual(Handler.objects.count(), 0)
        
    def test_delete_handler_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_detail_url, HandlerDetail, self.handler.pk)
        
    def test_delete_handler_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_detail_url(), HandlerDetail, self.bot.pk, self.handler.pk)
        
    def test_delete_handler_not_found(self):
        self._test_delete_detail_not_found(self._handler_detail_url(handler_pk=self.unlikely_id), HandlerDetail, self.bot.pk, self.unlikely_id)

        
class TestHandlerRequestParamsAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerRequestParamsAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.url_param = factories.UrlParamFactory(request=self.handler.request)
        self.header_param = factories.HeaderParamFactory(request=self.handler.request)
    
    def _handler_url_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/urlparams/' % (self.api, bot_pk, handler_pk)
    
    def _handler_url_param_detail_url(self, bot_pk=None, handler_pk=None, url_param_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not url_param_pk:
            url_param_pk = self.url_param.pk
        return '%s/bots/%s/handlers/%s/urlparams/%s/' % (self.api, bot_pk, handler_pk, url_param_pk)    
    
    def _handler_header_param_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/headerparams/' % (self.api, bot_pk, handler_pk)     
    
    def _handler_header_param_detail_url(self, bot_pk=None, handler_pk=None, header_param_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not header_param_pk:
            header_param_pk = self.header_param.pk
        return '%s/bots/%s/handlers/%s/headerparams/%s/' % (self.api, bot_pk, handler_pk, header_param_pk)            
        
    def assertUrlParam(self, id, created_at, updated_at, key, value_template, url_param=None):
        if not url_param:
            url_param = self.url_param
        self.assertEqual(url_param.key, key)
        self.assertEqual(url_param.value_template, value_template)
        self.assertMicrobotModel(id, created_at, updated_at, url_param)

    def assertHeaderParam(self, id, created_at, updated_at, key, value_template, header_param=None):
        if not header_param:
            header_param = self.header_param
        self.assertEqual(header_param.key, key)
        self.assertEqual(header_param.value_template, value_template)
        self.assertMicrobotModel(id, created_at, updated_at, header_param)
        
    def test_get_handler_url_params_ok(self):
        data = self._test_get_list_ok(self._handler_url_param_list_url())
        self.assertUrlParam(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_url_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_url_param_list_url())
        
    def test_post_handler_url_params_ok(self):
        data = {'key': self.handler.request.url_parameters.all()[0].key,
                'value_template': self.handler.request.url_parameters.all()[0].value_template}                         
        data = self._test_post_list_ok(self._handler_url_param_list_url(), UrlParam, data)
        new_url_param = UrlParam.objects.filter(request=self.handler.request)[0]
        self.assertUrlParam(None, self.url_param.created_at, self.url_param.updated_at, self.url_param.key, self.url_param.value_template, new_url_param)
        self.assertUrlParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'], new_url_param)
        
    def test_post_handler_url_params_validation_error(self):
        data = {'key': self.handler.request.url_parameters.all()[0].key,
                'value_template': '{{a'}                         
        errors = self._test_post_list_validation_error(self._handler_url_param_list_url(), UrlParam, data)
        self.assertNotEqual(None, errors['value_template'][0])
        
    def test_post_handler_url_params_not_auth(self):
        data = {'key': self.url_param.key,
                'value_template': self.url_param.value_template}
        self._test_post_list_not_auth(self._handler_url_param_list_url(), data)
            
    def test_get_handler_url_param_ok(self):
        data = self._test_get_detail_ok(self._handler_url_param_detail_url())
        self.assertUrlParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'])
        
    def test_get_handler_url_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_url_param_detail_url)
        
    def test_get_handler_url_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_url_param_detail_url())
        
    def test_get_handler_url_param_not_found(self):
        self._test_get_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id))
        
    def test_put_handler_url_param_ok(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        data = self._test_put_detail_ok(self._handler_url_param_detail_url(), data, UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        updated = UrlParam.objects.get(key=self.url_param.key)
        self.assertEqual(updated.value_template, 'new_url_param_value')
        self.assertUrlParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'], updated)
    
    def test_put_handler_url_param_validation_error(self):
        data = {'key': self.url_param.key,
                'value_template': '{{a'}
        response = self._test_put_detail_validation_error(self._handler_url_param_detail_url(), data, UrlParameterDetail, 
                                                          self.bot.pk, self.handler.pk, self.url_param.pk)
        self.assertNotEqual(None, response.data['value_template'][0])
     
    def test_put_handler_url_param_from_other_bot(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_from_other_bot(self._handler_url_param_detail_url, data, UrlParameterDetail, self.handler.pk, self.url_param.pk)
        
    def test_put_handler_url_param_not_auth(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_not_auth(self._handler_url_param_detail_url(), data, UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        
    def test_put_handler_url_param_not_found(self):
        data = {'key': self.url_param.key,
                'value_template': 'new_url_param_value'}
        self._test_put_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id), data, 
                                        UrlParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_url_param_ok(self):
        self._test_delete_detail_ok(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        self.assertEqual(UrlParam.objects.count(), 0)
        
    def test_delete_handler_url_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_url_param_detail_url, UrlParameterDetail, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_url_param_detail_url(), UrlParameterDetail, self.bot.pk, self.handler.pk, self.url_param.pk)
        
    def test_delete_handler_url_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_url_param_detail_url(url_param_pk=self.unlikely_id), 
                                           UrlParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
        
    def test_get_handler_header_params_ok(self):
        data = self._test_get_list_ok(self._handler_header_param_list_url())
        self.assertHeaderParam(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['key'], data[0]['value_template'])
        
    def test_get_handler_header_params_not_auth(self):
        self._test_get_list_not_auth(self._handler_header_param_list_url())
        
    def test_post_handler_header_params_ok(self):
        data = {'key': self.handler.request.header_parameters.all()[0].key,
                'value_template': self.handler.request.header_parameters.all()[0].value_template}                         
        data = self._test_post_list_ok(self._handler_header_param_list_url(), HeaderParam, data)
        new_header_param = HeaderParam.objects.filter(request=self.handler.request)[0]
        self.assertHeaderParam(None, self.header_param.created_at, self.header_param.updated_at, self.header_param.key, 
                               self.header_param.value_template, new_header_param)
        self.assertHeaderParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'], new_header_param)

    def test_post_handler_header_params_validation_error(self):
        data = {'key': self.handler.request.header_parameters.all()[0].key,
                'value_template': '{{a'}                         
        errors = self._test_post_list_validation_error(self._handler_header_param_list_url(), HeaderParam, data)
        self.assertNotEqual(None, errors['value_template'][0])
        
    def test_post_handler_header_params_not_auth(self):
        data = {'key': self.header_param.key,
                'value_template': self.header_param.value_template}
        self._test_post_list_not_auth(self._handler_header_param_list_url(), data)
        
    def test_get_handler_header_param_ok(self):
        data = self._test_get_detail_ok(self._handler_header_param_detail_url())
        self.assertHeaderParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'])
        
    def test_get_handler_header_param_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_header_param_detail_url)
        
    def test_get_handler_header_param_not_auth(self):
        self._test_get_detail_not_auth(self._handler_header_param_detail_url())
        
    def test_get_handler_header_param_not_found(self):
        self._test_get_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id))
        
    def test_put_handler_header_param_ok(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        data = self._test_put_detail_ok(self._handler_header_param_detail_url(), data, HeaderParameterDetail, 
                                        self.bot.pk, self.handler.pk, self.header_param.pk)
        updated = HeaderParam.objects.get(key=self.header_param.key)
        self.assertEqual(updated.value_template, 'new_header_param_value')
        self.assertHeaderParam(data['id'], data['created_at'], data['updated_at'], data['key'], data['value_template'], updated)

    def test_put_handler_header_param_validation_error(self):
        data = {'key': self.header_param.key,
                'value_template': '{{a'}
        response = self._test_put_detail_validation_error(self._handler_header_param_detail_url(), data, HeaderParameterDetail, 
                                                          self.bot.pk, self.handler.pk, self.header_param.pk)
        self.assertNotEqual(None, response.data['value_template'][0])
        
    def test_put_handler_header_param_from_other_bot(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_from_other_bot(self._handler_header_param_detail_url, data, HeaderParameterDetail, self.handler.pk, self.header_param.pk)
        
    def test_put_handler_header_param_not_auth(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_not_auth(self._handler_header_param_detail_url(), data, HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        
    def test_put_handler_header_param_not_found(self):
        data = {'key': self.header_param.key,
                'value_template': 'new_header_param_value'}
        self._test_put_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id), data, 
                                        HeaderParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_header_param_ok(self):
        self._test_delete_detail_ok(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        self.assertEqual(HeaderParam.objects.count(), 0)
        
    def test_delete_handler_header_param_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_header_param_detail_url, HeaderParameterDetail, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_header_param_detail_url(), HeaderParameterDetail, self.bot.pk, self.handler.pk, self.header_param.pk)
        
    def test_delete_handler_header_param_not_found(self):
        self._test_delete_detail_not_found(self._handler_header_param_detail_url(header_param_pk=self.unlikely_id), 
                                           HeaderParameterDetail, self.bot.pk, self.handler.pk, self.unlikely_id)

class TestHandlerSourceStatesAPI(BaseTestAPI):
    
    def setUp(self):
        super(TestHandlerSourceStatesAPI, self).setUp()
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.handler.source_states.add(self.state)
    
    def _handler_source_state_list_url(self, bot_pk=None, handler_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        return '%s/bots/%s/handlers/%s/sourcestates/' % (self.api, bot_pk, handler_pk)
    
    def _handler_source_state_detail_url(self, bot_pk=None, handler_pk=None, source_state_pk=None):
        if not bot_pk:
            bot_pk = self.bot.pk
        if not handler_pk:
            handler_pk = self.handler.pk
        if not source_state_pk:
            source_state_pk = self.state.pk
        return '%s/bots/%s/handlers/%s/sourcestates/%s/' % (self.api, bot_pk, handler_pk, source_state_pk)             
        
    def assertSourceStates(self, names, source_states=None):
        if not source_states:
            source_states = self.handler.source_states
        self.assertEqual(source_states.count(), len(names))
        for name in names:
            source_states.get(name=name)
    
    def assertState(self, id, created_at, updated_at, name, state=None):
        if not state:
            state = self.state
        self.assertEqual(state.name, name)
        self.assertMicrobotModel(id, created_at, updated_at, state)
    
    def test_get_handler_source_states_ok(self):
        data = self._test_get_list_ok(self._handler_source_state_list_url())
        self.assertState(data[0]['id'], data[0]['created_at'], data[0]['updated_at'], data[0]['name'])

    def test_get_handler_source_states_not_auth(self):
        self._test_get_list_not_auth(self._handler_source_state_list_url())
        
    def test_post_handler_source_states_ok(self):
        data = {'name': self.state.name}                         
        data = self._test_post_list_ok(self._handler_source_state_list_url(), State, data)
        new_source_states = Handler.objects.get(pk=self.handler.pk).source_states
        self.assertSourceStates([obj.name for obj in self.handler.source_states.all()], new_source_states)
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'], new_source_states.all()[0])
        
    def test_post_handler_source_states_not_auth(self):
        data = {'name': self.state.name}
        self._test_post_list_not_auth(self._handler_source_state_list_url(), data)
            
    def test_get_handler_source_state_ok(self):
        data = self._test_get_detail_ok(self._handler_source_state_detail_url())
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'])
        
    def test_get_handler_source_state_from_other_bot(self):
        self._test_get_detail_from_other_bot(self._handler_source_state_detail_url)
        
    def test_get_handler_source_state_not_auth(self):
        self._test_get_detail_not_auth(self._handler_source_state_detail_url())
        
    def test_get_handler_source_state_not_found(self):
        self._test_get_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id))
        
    def test_put_handler_source_state_ok(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}
        data = self._test_put_detail_ok(self._handler_source_state_detail_url(), data, SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        self.assertEqual(self.handler.source_states.count(), 1)
        self.assertEqual(self.handler.source_states.all()[0].name, 'new_state')
        self.assertState(data['id'], data['created_at'], data['updated_at'], data['name'], self.handler.source_states.all()[0])
  
    def test_put_handler_source_state_from_other_bot(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}
        self._test_put_detail_from_other_bot(self._handler_source_state_detail_url, data, SourceStateDetail, self.handler.pk, self.state.pk)
        
    def test_put_handler_source_state_not_auth(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}        
        self._test_put_detail_not_auth(self._handler_source_state_detail_url(), data, SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        
    def test_put_handler_source_state_not_found(self):
        new_state = factories.StateFactory(bot=self.bot,
                                           name="new_state")
        data = {'name': new_state.name}  
        self._test_put_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id), data, 
                                        SourceStateDetail, self.bot.pk, self.handler.pk, self.unlikely_id)
          
    def test_delete_handler_source_state_ok(self):
        self._test_delete_detail_ok(self._handler_source_state_detail_url(), SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        self.assertEqual(UrlParam.objects.count(), 0)
        
    def test_delete_handler_source_state_from_other_bot(self):
        self._test_delete_detail_from_other_bot(self._handler_source_state_detail_url, SourceStateDetail, self.handler.pk, self.state.pk)
        
    def test_delete_handler_source_state_not_auth(self):
        self._test_delete_detail_not_auth(self._handler_source_state_detail_url(), SourceStateDetail, self.bot.pk, self.handler.pk, self.state.pk)
        
    def test_delete_handler_source_state_not_found(self):
        self._test_delete_detail_not_found(self._handler_source_state_detail_url(source_state_pk=self.unlikely_id), 
                                           SourceStateDetail, self.bot.pk, self.handler.pk, self.unlikely_id)   