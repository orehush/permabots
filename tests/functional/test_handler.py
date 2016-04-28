#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Request, EnvironmentVar, TelegramChatState, Handler, KikChatState
from tests.models import Author, Book
from microbot.test import factories, testcases
from django.test import LiveServerTestCase
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.apps import apps
import json
from rest_framework import status
from unittest import skip

try:
    from unittest import mock
except ImportError:
    import mock  # noqa

ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))

class TestHandler(testcases.TelegramTestBot):
    
    author_get = {'in': '/authors',
                  'out': {'parse_mode': 'HTML',
                          'reply_markup': '',
                          'text': '<b>author1</b>'
                          }
                  }
             
    def test_no_handler(self):
        self._test_message(self.author_get, no_handler=True)
         
    def test_handler_disabled(self):
        self.handler = factories.HandlerFactory(bot=self.bot, enabled=False)
        self._test_message(self.author_get, no_handler=True)      
        
    def test_handler_in_other_state(self):
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern="/authors")
        self.handler.source_states.add(self.state)
        self.new_state = factories.StateFactory(bot=self.bot,
                                                name="state2")
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
        self.chat_state = factories.TelegramChatStateFactory(chat=self.chat,
                                                             state=self.new_state,
                                                             user=self.user)
        
        self._test_message(self.author_get, no_handler=True)
        
    def test_handler_in_other_state_when_no_chat_state(self):
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern="/authors")
        self.handler.source_states.add(self.state)
        self.chat = factories.TelegramChatAPIFactory(id=self.telegram_update.message.chat.id,
                                                     type=self.telegram_update.message.chat.type, 
                                                     title=self.telegram_update.message.chat.title,
                                                     username=self.telegram_update.message.chat.username,
                                                     first_name=self.telegram_update.message.chat.first_name,
                                                     last_name=self.telegram_update.message.chat.last_name)
        
        self._test_message(self.author_get, no_handler=True)
            
    def test_handler_priority(self):
        self.handler1 = factories.HandlerFactory(bot=self.bot,
                                                 name="handler1",
                                                 priority=1)
        self.handler2 = factories.HandlerFactory(bot=self.bot,
                                                 name="handler2",
                                                 priority=2)
        self.assertEqual(Handler.objects.all()[0], self.handler2)
        self.assertEqual(Handler.objects.all()[1], self.handler1)
        
    def test_handler_request_no_cascade(self):
        self.handler = factories.HandlerFactory(bot=self.bot)
        self.assertEqual(Handler.objects.count(), 1)
        Request.objects.all().delete()
        self.assertEqual(Handler.objects.count(), 1)        
                
    def test_telegram_no_text_message(self):
        update = json.loads(self.telegram_update.to_json())
        update['message'].pop('text')
        response = self.client.post(self.telegram_webhook_url, json.dumps(update), **self.kwargs)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        
    def test_kik_no_text_message(self):
        def to_send(message):
            from time import mktime
            if message.timestamp:
                message.timestamp = int(mktime(message.timestamp.timetuple()))
            message.id = str(message.id)
            return json.dumps(message.to_json())
        message = json.loads(to_send(self.kik_message))
        message.pop('body')
        message['type'] = "sticker"
        messages = {'messages': [message]}
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()):
            response = self.client.post(self.kik_webhook_url, json.dumps(messages), **self.kwargs)
            self.assertEqual(status.HTTP_200_OK, response.status_code)

    @skip("verify removed")   
    def test_kik_not_verified(self):
        def to_send(message):
            from time import mktime
            if message.timestamp:
                message.timestamp = int(mktime(message.timestamp.timetuple()))
            message.id = str(message.id)
            return json.dumps(message.to_json())
        response = self.client.post(self.kik_webhook_url, to_send(self.kik_message), **self.kwargs)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        
class TestRequests(LiveServerTestCase, testcases.TelegramTestBot):
    
    author_get = {'in': '/authors',
                  'out': {'parse_mode': 'HTML',
                          'reply_markup': '',
                          'text': '<b>author1</b>'
                          }
                  }
    
    author_get_pattern = {'in': '/authors@1',
                          'out': {'parse_mode': 'HTML',
                                  'reply_markup': '',
                                  'text': '<b>author1</b>'
                                  }
                          }
    
    author_get_pattern_not_found = {'in': '/authors@99',
                                    'out': {'parse_mode': 'HTML',
                                            'reply_markup': '',
                                            'text': 'Not found'
                                            }
                                    }
    
    author_get_keyboard = {'in': '/authors',
                           'out': {'parse_mode': 'HTML',
                                   'reply_markup': 'author1',
                                   'text': '<b>author1</b>'
                                   }
                           }
    
    author_post_pattern = {'in': '/authors',
                           'out': {'parse_mode': 'HTML',
                                   'reply_markup': '',
                                   'text': '<b>author1</b> created'
                                   }
                           }
    
    author_put_pattern = {'in': '/authors@1',
                          'out': {'parse_mode': 'HTML',
                                  'reply_markup': '',
                                  'text': '<b>author2</b> updated'
                                  }
                          }
    
    author_delete_pattern = {'in': '/authors_delete@1',
                             'out': {'parse_mode': 'HTML',
                                     'reply_markup': '',
                                     'text': 'Author 1 deleted'
                                     }
                             }
    
    author_get_with_environment_var = {'in': '/authors',
                                       'out': {'parse_mode': 'HTML',
                                               'reply_markup': '',
                                               'text': 'myebookshop:<b>author1</b>'
                                               }
                                       }
    
    author_get_with_url_parameters = {'in': '/authors_name@author1',
                                      'out': {'parse_mode': 'HTML',
                                              'reply_markup': '',
                                              'text': '<b>author1</b>'
                                              }
                                      }
    
    author_post_header_error = {'in': '/authors',
                                'out': {'parse_mode': 'HTML',
                                        'reply_markup': '',
                                        'text': 'not created'
                                        }
                                }
    
    book_get_authorized = {'in': '/books',
                           'out': {'parse_mode': 'HTML',
                                   'reply_markup': '',
                                   'text': '<b>ebook1</b>'
                                   }
                           }
    
    book_get_not_authorized = {'in': '/books',
                               'out': {'parse_mode': 'HTML',
                                       'reply_markup': '',
                                       'text': 'no books for you'
                                       }
                               }
    
    author_post_data_template = {'in': '/authorscreate@author2',
                                 'out': {'parse_mode': 'HTML',
                                         'reply_markup': '',
                                         'text': '<b>author2</b> created'
                                         }
                                 }
    
    author_put_data_template = {'in': '/authorsupdate@1@author2',
                                'out': {'parse_mode': 'HTML',
                                        'reply_markup': '',
                                        'text': '<b>author2</b> updated'
                                        }
                                }
    
    message_as_part_of_context = {'in': '/authors@1',
                                  'out': {'parse_mode': 'HTML',
                                          'reply_markup': '',
                                          'text': '<b>author2</b> updated by first_name_'
                                          }
                                  }
    
    no_request = {'in': '/norequest',
                  'out': {'parse_mode': 'HTML',
                          'reply_markup': '',
                          'text': 'Just plain response'
                          }
                  }
    
    author_get_with_state_context = {'in': '/authors',
                                     'out': {'parse_mode': 'HTML',
                                             'reply_markup': '',
                                             'text': '<b>author1</b>in_context'
                                             }
                                     }
    
    author_get_with_emoji = {'in': '/authors',
                             'out': {'parse_mode': 'HTML',
                                     'reply_markup': '',
                                     'text': u'<b>author1</b> \U0001F4A9'
                                     }
                             }
    
    def test_get_request(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_get)
   
    def test_get_pattern_command(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b>',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                response=self.response,
                                                request=self.request)
        self._test_message(self.author_get_pattern)
          
    def test_get_request_with_keyboard(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='[[{% for author  in response.data %}"{{author.name}}"{% endfor %}]]')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_get_keyboard)
      
    def test_post_request(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                data='{"name": "author1"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> created',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_post_pattern)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author1")
          
    def test_put_request(self):
        author = Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.PUT,
                                                data='{"name": "author2"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> updated',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_put_pattern)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author2")
          
    def test_delete_request(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.DELETE)
        self.response = factories.ResponseFactory(text_template='Author {{ pattern.id }} deleted',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors_delete@(?P<id>\d+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_delete_pattern)
        self.assertEqual(Author.objects.count(), 0)
  
    def test_environment_vars(self):
        EnvironmentVar.objects.create(bot=self.bot,
                                      key="shop", 
                                      value="myebookshop")
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{{env.shop}}:{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_get_with_environment_var)
         
    def test_url_parameters(self):
        Author.objects.create(name="author1")
        Author.objects.create(name="author2")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.url_param = factories.UrlParamFactory(request=self.request,
                                                   key='name',
                                                   value_template='{{pattern.name}}')
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors_name@(?P<name>\w+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_get_with_url_parameters)
        
    def test_header_parameters(self):
        # Unsupported media type 415. Author not created
        EnvironmentVar.objects.create(bot=self.bot,
                                      key="content_type", 
                                      value="application/xml")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                data='{"name": "author1"}')
        self.header_param = factories.HeaderParamFactory(request=self.request,
                                                         key='Content-Type',
                                                         value_template='{{env.content_type}}')
        self.response = factories.ResponseFactory(text_template='{% if response.name %}<b>{{response.data.name}}</b> created{% else %}not created{% endif %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_post_header_error)
        self.assertEqual(Author.objects.count(), 0)
        
    def test_header_authentitcation(self):
        user = ModelUser.objects.create_user(username='username',
                                             email='username@test.com',
                                             password='password')
        token = Token.objects.get(user=user)
        Book.objects.create(title="ebook1", owner=user)
        EnvironmentVar.objects.create(bot=self.bot,
                                      key="token", 
                                      value=token)
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/books/',
                                                method=Request.GET)
        self.header_param = factories.HeaderParamFactory(request=self.request,
                                                         key='Authorization',
                                                         value_template='Token {{env.token}}')
        self.response = factories.ResponseFactory(text_template='''{% if response.data %}{% for book in response.data %}<b>{{book.title}}</b>{% endfor %}
                                                                {% else %}not books{% endif %}''',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(
            bot=self.bot,
            pattern='/books',
            request=self.request,
            response=self.response)
        self._test_message(self.book_get_authorized)
        
    def test_header_not_authenticated(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/books/',
                                                method=Request.GET)
        self.header_param = factories.HeaderParamFactory(request=self.request,
                                                         key='Authorization',
                                                         value_template='Token erroneustoken')
        self.response = factories.ResponseFactory(text_template='''{% if response.status == 401 %}no books for you{% else %}{% for book in response.data %}<b>{{book.title}}</b>{% endfor %}
                                                                {% endif %}''',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(
            bot=self.bot,
            pattern='/books',
            request=self.request,
            response=self.response)
        self._test_message(self.book_get_not_authorized)   
        
    def test_post_data_template(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                data='{"name":"{{pattern.name}}"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> created',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authorscreate@(?P<name>\w+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_post_data_template)
        self.assertEqual(Author.objects.all()[0].name, 'author2')
        
    def test_put_data_template(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.PUT,
                                                data='{"name":"{{pattern.name}}"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> updated',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authorsupdate@(?P<id>\d+)@(?P<name>\w+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_put_data_template)
        self.assertEqual(Author.objects.all()[0].name, 'author2')
        
    def test_patch_data_template(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.PATCH,
                                                data='{"name":"{{pattern.name}}"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> updated',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authorsupdate@(?P<id>\d+)@(?P<name>\w+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_put_data_template)
        self.assertEqual(Author.objects.all()[0].name, 'author2')
        
    def test_message_as_part_of_context(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.PUT,
                                                data='{"name": "author2"}')
        self.response = factories.ResponseFactory(text_template='<b>{{response.data.name}}</b> updated by {{message.from_user.first_name}}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.message_as_part_of_context)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author2")
        
    def test_handler_with_state(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
        self.handler.source_states.add(self.state)
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
        self.chat_state = factories.TelegramChatStateFactory(chat=self.chat,
                                                             state=self.state,
                                                             user=self.user)
        
        self._test_message(self.author_get)
        self.assertEqual(TelegramChatState.objects.get(chat=self.chat).state, self.state_target)
        state_context = TelegramChatState.objects.get(chat=self.chat).ctx
        self.assertEqual(state_context['state1']['pattern'], {})
        self.assertEqual(state_context['state1']['response']['data'][0], {'name': 'author1'})
        self.assertEqual(None, state_context['state1'].get('state_context', None))
        
    def test_handler_with_state_no_to_target_beacuse_no_success(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{pattern.id}}/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% if response.status == 404 %}Not found{% else %}<b>{{response.data.name}}</b>{% endif %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                response=self.response,
                                                request=self.request)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
        self.handler.source_states.add(self.state)
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
        self.chat_state = factories.TelegramChatStateFactory(chat=self.chat,
                                                             state=self.state,
                                                             user=self.user)
        
        self._test_message(self.author_get_pattern_not_found)
        self.assertEqual(TelegramChatState.objects.get(chat=self.chat).state, self.state)

    def test_handler_with_state_still_no_chatstate(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
        self.chat = factories.TelegramChatAPIFactory(id=self.telegram_update.message.chat.id,
                                                     type=self.telegram_update.message.chat.type, 
                                                     title=self.telegram_update.message.chat.title,
                                                     username=self.telegram_update.message.chat.username,
                                                     first_name=self.telegram_update.message.chat.first_name,
                                                     last_name=self.telegram_update.message.chat.last_name)
        
        self._test_message(self.author_get)
        self.assertEqual(TelegramChatState.objects.get(chat=self.chat).state, self.state_target)
        state_context = TelegramChatState.objects.get(chat=self.chat).ctx
        self.assertEqual(state_context['_start']['pattern'], {})
        self.assertEqual(state_context['_start']['response']['data'][0], {'name': 'author1'})
        self.assertEqual(None, state_context['_start'].get('state_context', None))
        
    def test_handler_with_state_still_no_chatstate_but_with_state_from_other_bot(self):
        self.other_telegram_bot = factories.TelegramBotFactory(token='190880460:AAELDdTxhhfPbtPRyC59qPaVF5VBX4VGVes')
        self.other_bot = factories.BotFactory(telegram_bot=self.other_telegram_bot)
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
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
        self.other_bot_same_name = factories.StateFactory(bot=self.other_bot,
                                                          name=self.state.name)
        self.other_bot_chat_state = factories.TelegramChatStateFactory(chat=self.chat,
                                                                       state=self.other_bot_same_name,
                                                                       user=self.user)
        self._test_message(self.author_get)
        self.assertEqual(TelegramChatState.objects.count(), 2)
        self.assertEqual(TelegramChatState.objects.get(chat=self.chat, state__bot=self.bot).state, self.state_target)
        state_context = TelegramChatState.objects.get(chat=self.chat, state__bot=self.bot).ctx
        self.assertEqual(state_context['_start']['pattern'], {})
        self.assertEqual(state_context['_start']['response']['data'][0], {'name': 'author1'})
        self.assertEqual(None, state_context['_start'].get('state_context', None))
        
    def test_get_request_with_more_priority(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.request_priority = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                         method=Request.GET)
        self.response = factories.ResponseFactory(text_template='Impossible template',
                                                  keyboard_template='')
        self.response_priority = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b>{% endfor %}',
                                                           keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response,
                                                priority=1)
        self.handler_priority = factories.HandlerFactory(bot=self.bot,
                                                         pattern='/authors',
                                                         request=self.request_priority,
                                                         response=self.response_priority,
                                                         priority=2)
        self._test_message(self.author_get)
        
    def test_no_request(self):
        self.response = factories.ResponseFactory(text_template='Just plain response',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/norequest',
                                                response=self.response)      
        
    def test_handler_with_state_context(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        text_template = '{% for author in response.data %}<b>{{author.name}}</b>{{state_context.prev_state.var}}{% endfor %}'
        self.response = factories.ResponseFactory(text_template=text_template,
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
        self.handler.source_states.add(self.state)
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
        self.chat_state = factories.TelegramChatStateFactory(chat=self.chat,
                                                             state=self.state,
                                                             user=self.user,
                                                             context='{"prev_state": {"var":"in_context"}}')
        self.assertEqual(json.loads(self.chat_state.context), self.chat_state.ctx)
        self._test_message(self.author_get_with_state_context)
        self.assertEqual(TelegramChatState.objects.get(chat=self.chat).state, self.state_target)
        
    def test_get_with_emoji(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}<b>{{author.name}}</b> {{emoji.pile_of_poo}}{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self._test_message(self.author_get_with_emoji)
        
    def test_split_message(self):
        with mock.patch(self.send_message_to_patch, callable=mock.MagicMock()) as mock_send:
            response = 'a' * 4096 + 'b' * 100
            built_keyboard = self.bot.telegram_bot.build_keyboard("[['menu']]")
            self.bot.telegram_bot.send_message(101, response, built_keyboard, None, user="user1")
            self.assertEqual(2, mock_send.call_count)
            for call_args in mock_send.call_args_list:
                args, kwargs = mock_send.call_args_list[0]
                self.assertEqual('a'*4096, kwargs['text'])
                self.assertEqual(None, kwargs['reply_markup'])
                args, kwargs = mock_send.call_args_list[1]
                self.assertEqual('b'*100, kwargs['text'])
                self.assertEqual(built_keyboard, kwargs['reply_markup'])
        
        
class TestKikRequests(LiveServerTestCase, testcases.KikTestBot):
    
    author_get = {'in': '/authors',
                  'out': {'body': 'author1',
                          'reply_markup': "menu1"
                          }
                  }
    
    author_get_with_emoji = {'in': '/authors',
                             'out': {'body': u'author1 \U0001F4A9',
                                     'reply_markup': "menu1"
                                     }
                             }
    
    author_get_no_menu = {'in': '/authors',
                          'out': {'body': 'author1',
                                  'reply_markup': ""
                                  }
                          }
    
    start = {'in': '',
             'out': {'body': 'Wellcome',
                     'reply_markup': ''}}
    
    def test_get_request(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='''{% for author in response.data %}{% if service == "kik" %}
                                                                {{author.name}}{% endif %}{% endfor %}''',
                                                  keyboard_template='[["menu1"],["menu2"]]')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()) as mock_verify:
            mock_verify.return_value = True
            self._test_message(self.author_get)
            
    def test_start(self):
        self.response = factories.ResponseFactory(text_template='Wellcome',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/start',
                                                response=self.response)
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()) as mock_verify:
            mock_verify.return_value = True
            self.kik_message = factories.KikStartMessageLibFactory()
            self.message_api = {'messages': [self.kik_message]}
            self._test_message(self.start)
                        
    def test_handler_with_state(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='{% for author in response.data %}{{author.name}}{% endfor %}',
                                                  keyboard_template='')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        self.state = factories.StateFactory(bot=self.bot,
                                            name="state1")
        self.state_target = factories.StateFactory(bot=self.bot,
                                                   name="state2")
        self.handler.target_state = self.state_target
        self.handler.save()
        self.handler.source_states.add(self.state)
        self.user = factories.KikUserAPIFactory(username=self.kik_message.from_user)
        self.chat = factories.KikChatAPIFactory(id=self.kik_message.chat_id)
        self.chat.participants = [self.user]
        self.chat_state = factories.KikChatStateFactory(chat=self.chat,
                                                        state=self.state,
                                                        user=self.user)
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()) as mock_verify:
            mock_verify.return_value = True
            self._test_message(self.author_get_no_menu)
            self.assertEqual(KikChatState.objects.get(chat=self.chat).state, self.state_target)
            state_context = KikChatState.objects.get(chat=self.chat).ctx
            self.assertEqual(state_context['state1']['pattern'], {})
            self.assertEqual(state_context['state1']['response']['data'][0], {'name': 'author1'})
            self.assertEqual(None, state_context['state1'].get('service', None))
            self.assertEqual(None, state_context['state1'].get('state_context', None))
            
    def test_kik_limit_keyboard_ok(self):
        keyboard = "[" + str(["menu_"+str(e) for e in range(1, 21)]) + "]"
        built_keyboard = self.bot.kik_bot.build_keyboard(keyboard)
        self.assertEqual(20, len(built_keyboard))
        
    def test_kik_limit_keyboard_truncated_by_word(self):
        keyboard = "[" + str(["menu_"+str(e) for e in range(1, 21)]) + "]"
        built_keyboard = self.bot.kik_bot.build_keyboard(keyboard)
        self.assertEqual(20, len(built_keyboard))
        
    def test_get_with_emoji(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.response = factories.ResponseFactory(text_template='''{% for author in response.data %}{% if service == "kik" %}
                                                                {{author.name}} {{emoji.pile_of_poo}}{% endif %}{% endfor %}''',
                                                  keyboard_template='[["menu1"],["menu2"]]')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response=self.response)
        with mock.patch('kik.api.KikApi.verify_signature', callable=mock.MagicMock()) as mock_verify:
            mock_verify.return_value = True
            self._test_message(self.author_get_with_emoji)
            
    def test_split_message(self):
        with mock.patch(self.send_message_to_patch, callable=mock.MagicMock()) as mock_send:
            response = 'a' * 100 + 'b' * 50
            chat_id = "chatid"
            keyboard = "[" + str(["menu_"+str(e) for e in range(1, 21)]) + "]"
            built_keyboard = self.bot.kik_bot.build_keyboard(keyboard)
            self.bot.kik_bot.send_message(chat_id, response, built_keyboard, None, user="user1")
            self.assertEqual(1, mock_send.call_count)
            for call_args in mock_send.call_args_list:
                args, kwargs = call_args
                messages = args[0]
                self.assertEqual(2, len(messages))
                self.assertEqual('a'*100, messages[0].body)
                self.assertEqual(0, len(messages[0].keyboards))
                self.assertEqual('b'*50, messages[1].body)
                self.assertEqual(built_keyboard, messages[1].keyboards[0].responses)