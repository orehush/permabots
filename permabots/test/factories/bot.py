# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from permabots.models import Bot, TelegramBot, KikBot, MessengerBot
from permabots.test.factories import UserFactory

class TelegramBotFactory(DjangoModelFactory):
    class Meta:
        model = TelegramBot
    token = "204840063:AAGKVVNf0HUTFoQKcgmLrvPv4tyP8xRCkFc"
    
class KikBotFactory(DjangoModelFactory):
    class Meta:
        model = KikBot
    username = 'Permatest'
    api_key = '605c50e6-9ef7-4e71-8538-d72e2489a7b5'
    
class MessengerBotFactory(DjangoModelFactory):
    class Meta:
        model = MessengerBot
    token = 'EAAO4bzdZBWZAABAO7TNopLq0v29dhCvoZAnZBaImXkBDiS23sblQb6nhThn4TByZBifvpuJGXZChXWt3wP2PcCXeVrXJHlcgMlNsurEgAIz419d4KkoCuvEeaLlwwkZBFpoirIBwNsgJZCtaiaH9dPC4m0Tit1wKN2CEAxAfR0V9eQZDZD'  # noqa
    
class BotFactory(DjangoModelFactory):
    class Meta:
        model = Bot
    name = Sequence(lambda n: 'name%d' % n)
    owner = SubFactory(UserFactory)
    telegram_bot = SubFactory(TelegramBotFactory)
    kik_bot = SubFactory(KikBotFactory)
    messenger_bot = SubFactory(MessengerBotFactory)