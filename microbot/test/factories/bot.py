# coding=utf-8
from factory import DjangoModelFactory, SubFactory
from microbot.models import Bot
from microbot.test.factories import UserFactory

class BotFactory(DjangoModelFactory):
    class Meta:
        model = Bot
    token = "204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc"
    owner = SubFactory(UserFactory)