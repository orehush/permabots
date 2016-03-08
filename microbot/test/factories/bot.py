# coding=utf-8
from factory import DjangoModelFactory 
from microbot.models import Bot


class BotFactory(DjangoModelFactory):
    class Meta:
        model = Bot
    token = "204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc"