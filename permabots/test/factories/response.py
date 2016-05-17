# coding=utf-8
from factory import DjangoModelFactory
from permabots.models import Response

class ResponseFactory(DjangoModelFactory):
    class Meta:
        model = Response
    text_template = '<a href="{{ html_url }}">{{ login }}</a>\n<b>{{ location }}</b>:<i>{{ created_at }}</i>'
    keyboard_template = '[["followers", "{{ name }}"]]'