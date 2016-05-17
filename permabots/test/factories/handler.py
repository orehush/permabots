# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from permabots.models import Handler, Request, UrlParam, HeaderParam
from permabots.test.factories import BotFactory, ResponseFactory


class RequestFactory(DjangoModelFactory):
    class Meta:
        model = Request
    url_template = "https://api.github.com/users/jlmadurga"
    method = Request.GET
    
class UrlParamFactory(DjangoModelFactory):
    class Meta:
        model = UrlParam
    key = Sequence(lambda n: 'key%d' % n)
    value_template = Sequence(lambda n: '{{value%d}}' % n)
    request = SubFactory(RequestFactory)
    
class HeaderParamFactory(DjangoModelFactory):
    class Meta:
        model = HeaderParam
    key = Sequence(lambda n: 'key%d' % n)
    value_template = Sequence(lambda n: '{{value%d}}' % n)
    request = SubFactory(RequestFactory)


class HandlerFactory(DjangoModelFactory):
    class Meta:
        model = Handler
    bot = SubFactory(BotFactory)
    name = Sequence(lambda n: 'name%d' % n)
    pattern = "/github_user" 
    request = SubFactory(RequestFactory)
    response = SubFactory(ResponseFactory)