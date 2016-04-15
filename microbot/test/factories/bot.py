# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from microbot.models import Bot, TelegramBot
from microbot.test.factories import UserFactory

class TelegramBotFactory(DjangoModelFactory):
    class Meta:
        model = TelegramBot
    token = "204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc"
    
class BotFactory(DjangoModelFactory):
    class Meta:
        model = Bot
    name = Sequence(lambda n: 'name%d' % n)
    owner = SubFactory(UserFactory)
    telegram_bot = SubFactory(TelegramBotFactory)