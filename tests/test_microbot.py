#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, Request, EnvironmentVar
from tests.models import Author, Book
from microbot.test import factories, testcases
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from rest_framework import status
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.apps import apps
try:
    from unittest import mock
except ImportError:
    import mock  # noqa

ModelUser = apps.get_model(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))

class TestBot(testcases.BaseTestBot):
       
    def test_enable_webhook(self):
        self.assertTrue(self.bot.enabled)
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertIn(reverse('microbot:telegrambot', kwargs={'token': self.bot.token}), 
                          kwargs['webhook_url'])
               
    def test_disable_webhook(self):
        self.bot.enabled = False
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()) as mock_setwebhook:
            self.bot.save()
            args, kwargs = mock_setwebhook.call_args
            self.assertEqual(1, mock_setwebhook.call_count)
            self.assertEqual(None, kwargs['webhook_url'])
               
    def test_bot_user_api(self):
        with mock.patch("telegram.bot.Bot.setWebhook", callable=mock.MagicMock()):
            self.bot.user_api = None
            self.bot.save()
            self.assertEqual(self.bot.user_api.first_name, u'Microbot_test')
            self.assertEqual(self.bot.user_api.username, u'Microbot_test_bot')
               
    def test_no_bot_associated(self):
        Bot.objects.all().delete()
        self.assertEqual(0, Bot.objects.count())
        response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
          
    def test_bot_disabled(self):
        self.bot.enabled = False
        self.bot.save()
        response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)        
       
    def test_not_valid_update(self):
        del self.update.message
        response = self.client.post(self.webhook_url, self.update.to_json(), **self.kwargs)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
         
         
class TestHandler(testcases.BaseTestBot):
    
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
         
class TestRequests(LiveServerTestCase, testcases.BaseTestBot):
    
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
                                       'text': 'not books'
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
    
    update_as_part_of_context = {'in': '/authors@1',
                                 'out': {'parse_mode': 'HTML',
                                         'reply_markup': '',
                                         'text': '<b>author2</b> updated by first_name_'
                                         }
                                 }
    
    def test_get_request(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='{% for author in response.list %}<b>{{author.name}}</b>{% endfor %}',
                                                response_keyboard_template='')
        self._test_message(self.author_get)
   
    def test_get_pattern_command(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{url.id}}/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                response_text_template='<b>{{response.name}}</b>',
                                                response_keyboard_template='',
                                                request=self.request)
        self._test_message(self.author_get_pattern)
          
    def test_get_request_with_keyboard(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='{% for author in response.list %}<b>{{author.name}}</b>{% endfor %}',
                                                response_keyboard_template='[[{% for author  in response.list %}"{{author.name}}"{% endfor %}]]')
        self._test_message(self.author_get_keyboard)
      
    def test_post_request(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                data='{"name": "author1"}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='<b>{{response.name}}</b> created',
                                                response_keyboard_template='')
        self._test_message(self.author_post_pattern)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author1")
          
    def test_put_request(self):
        author = Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{url.id}}/',
                                                method=Request.PUT,
                                                data='{"name": "author2"}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                request=self.request,
                                                response_text_template='<b>{{response.name}}</b> updated',
                                                response_keyboard_template='')
        self._test_message(self.author_put_pattern)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author2")
          
    def test_delete_request(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{url.id}}/',
                                                method=Request.DELETE)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors_delete@(?P<id>\d+)',
                                                request=self.request,
                                                response_text_template='Author {{ url.id }} deleted',
                                                response_keyboard_template='')
        self._test_message(self.author_delete_pattern)
        self.assertEqual(Author.objects.count(), 0)
  
    def test_environment_vars(self):
        EnvironmentVar.objects.create(bot=self.bot,
                                      key="shop", 
                                      value="myebookshop")
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='{{env.shop}}:{% for author in response.list %}<b>{{author.name}}</b>{% endfor %}',
                                                response_keyboard_template='')
        self._test_message(self.author_get_with_environment_var)
         
    def test_url_parameters(self):
        Author.objects.create(name="author1")
        Author.objects.create(name="author2")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.url_param = factories.UrlParamFactory(request=self.request,
                                                   key='name',
                                                   value_template='{{url.name}}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors_name@(?P<name>\w+)',
                                                request=self.request,
                                                response_text_template='{% for author in response.list %}<b>{{author.name}}</b>{% endfor %}',
                                                response_keyboard_template='')
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
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='{% if response.name %}<b>{{response.name}}</b> created{% else %}not created{% endif %}',
                                                response_keyboard_template='')
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
        self.handler = factories.HandlerFactory(
            bot=self.bot,
            pattern='/books',
            request=self.request,
            response_text_template='''{% if response.list %}{% for book in response.list %}<b>{{book.title}}</b>{% endfor %}
                                    {% else %}not books{% endif %}''',
            response_keyboard_template='')
        self._test_message(self.book_get_authorized)
        
    def test_header_not_authenticated(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/books/',
                                                method=Request.GET)
        self.header_param = factories.HeaderParamFactory(request=self.request,
                                                         key='Authorization',
                                                         value_template='Token erroneustoken')
        self.handler = factories.HandlerFactory(
            bot=self.bot,
            pattern='/books',
            request=self.request,
            response_text_template='''{% if response.list %}{% for book in response.list %}<b>{{book.title}}</b>{% endfor %}
                                   {% else %}not books{% endif %}''',
            response_keyboard_template='')
        self._test_message(self.book_get_not_authorized)   
        
    def test_post_data_template(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                data='{"name":"{{url.name}}"}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authorscreate@(?P<name>\w+)',
                                                request=self.request,
                                                response_text_template='<b>{{response.name}}</b> created',
                                                response_keyboard_template='')
        self._test_message(self.author_post_data_template)
        self.assertEqual(Author.objects.all()[0].name, 'author2')
        
    def test_put_data_template(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{url.id}}/',
                                                method=Request.PUT,
                                                data='{"name":"{{url.name}}"}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authorsupdate@(?P<id>\d+)@(?P<name>\w+)',
                                                request=self.request,
                                                response_text_template='<b>{{response.name}}</b> updated',
                                                response_keyboard_template='')
        self._test_message(self.author_put_data_template)
        self.assertEqual(Author.objects.all()[0].name, 'author2')
        
    def test_update_as_part_of_context(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{url.id}}/',
                                                method=Request.PUT,
                                                data='{"name": "author2"}')
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                request=self.request,
                                                response_text_template='<b>{{response.name}}</b> updated by {{update.message.from_user.first_name}}',
                                                response_keyboard_template='')
        self._test_message(self.update_as_part_of_context)
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "author2")
