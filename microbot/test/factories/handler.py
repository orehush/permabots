# coding=utf-8
from factory import DjangoModelFactory, SubFactory
from microbot.models import Handler, Request
from microbot.test.factories import BotFactory


class RequestFactory(DjangoModelFactory):
    class Meta:
        model = Request
    url_template = "https://api.github.com/users/jlmadurga"
    method = Request.GET


class HandlerFactory(DjangoModelFactory):
    class Meta:
        model = Handler
    bot = SubFactory(BotFactory)
    pattern = "/github_user" 
    request = SubFactory(RequestFactory)
    response_text_template = '<a href="{{ html_url }}">{{ login }}</a>\n<b>{{ location }}</b>:<i>{{ created_at }}</i>'
    response_keyboard_template = '[["followers", "{{ name }}"]]'