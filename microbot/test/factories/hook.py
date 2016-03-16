# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from microbot.models import Hook, Recipient
from microbot.test.factories import BotFactory, ResponseFactory

class HookFactory(DjangoModelFactory):
    class Meta:
        model = Hook
    bot = SubFactory(BotFactory)
    key = Sequence(lambda n: 'key_%d' % n)
    response = SubFactory(ResponseFactory)
    
class RecipientFactory(DjangoModelFactory):
    class Meta:
        model = Recipient
    id = Sequence(lambda n: n+1)
    hook = SubFactory(HookFactory)