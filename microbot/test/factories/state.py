# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from microbot.models import State, TelegramChatState
from microbot.test.factories import ChatLibFactory, BotFactory

class StateFactory(DjangoModelFactory):
    class Meta:
        model = State
    bot = SubFactory(BotFactory)
    name = Sequence(lambda n: 'state_%d' % n)
    
class TelegramChatStateFactory(DjangoModelFactory):
    class Meta:
        model = TelegramChatState
    chat = SubFactory(ChatLibFactory)
    state = SubFactory(StateFactory)