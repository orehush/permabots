#!/usr/bin/env python
# -*- coding: utf-8 -*-
from microbot.models import Bot, Request
from tests.models import Author
from microbot.test import factories, testcases
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from rest_framework import status
try:
    from unittest import mock
except ImportError:
    import mock  # noqa


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
         
class TestPost(LiveServerTestCase, testcases.BaseTestBot):
    
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
    
    def test_simple_command(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors',
                                                request=self.request,
                                                response_text_template='{% for author in response.list %}<b>{{author.name}}</b>{% endfor %}',
                                                response_keyboard_template='')
        self._test_message(self.author_get)
 
    def test_pattern_command(self):
        Author.objects.create(name="author1")
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{id}}/',
                                                method=Request.GET)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors@(?P<id>\d+)',
                                                response_text_template='<b>{{response.name}}</b>',
                                                response_keyboard_template='',
                                                request=self.request)
        self._test_message(self.author_get_pattern)
    
    def test_post_request(self):
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/',
                                                method=Request.POST,
                                                content_type="application/json",
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
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{id}}/',
                                                method=Request.PUT,
                                                content_type="application/json",
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
        self.request = factories.RequestFactory(url_template=self.live_server_url + '/api/authors/{{id}}/',
                                                method=Request.DELETE)
        self.handler = factories.HandlerFactory(bot=self.bot,
                                                pattern='/authors_delete@(?P<id>\d+)',
                                                request=self.request,
                                                response_text_template='Author {{ url.id }} deleted',
                                                response_keyboard_template='')
        self._test_message(self.author_delete_pattern)
        self.assertEqual(Author.objects.count(), 0)