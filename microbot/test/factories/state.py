# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from microbot.models import State, ChatState
from microbot.test.factories import ChatLibFactory, BotFactory

class StateFactory(DjangoModelFactory):
    class Meta:
        model = State
    bot = SubFactory(BotFactory)
    name = Sequence(lambda n: 'state_%d' % n)
    
class ChatStateFactory(DjangoModelFactory):
    class Meta:
        model = ChatState
    chat = SubFactory(ChatLibFactory)
    state = SubFactory(StateFactory)