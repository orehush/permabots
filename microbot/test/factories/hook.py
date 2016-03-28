# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from microbot.models import Hook, Recipient
from microbot.test.factories import BotFactory, ResponseFactory

class HookFactory(DjangoModelFactory):
    class Meta:
        model = Hook
    bot = SubFactory(BotFactory)
    name = Sequence(lambda n: 'name_%d' % n)
    key = Sequence(lambda n: 'key_%d' % n)
    response = SubFactory(ResponseFactory)
    
class RecipientFactory(DjangoModelFactory):
    class Meta:
        model = Recipient
    chat_id = Sequence(lambda n: n+1)
    name = Sequence(lambda n: 'name_%d' % n)
    hook = SubFactory(HookFactory)