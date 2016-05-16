# coding=utf-8
from factory import DjangoModelFactory, SubFactory, Sequence
from permabots.models import Hook, TelegramRecipient, KikRecipient, MessengerRecipient
from permabots.test.factories import BotFactory, ResponseFactory

class HookFactory(DjangoModelFactory):
    class Meta:
        model = Hook
    bot = SubFactory(BotFactory)
    name = Sequence(lambda n: 'name_%d' % n)
    key = Sequence(lambda n: 'key_%d' % n)
    response = SubFactory(ResponseFactory)
    
class TelegramRecipientFactory(DjangoModelFactory):
    class Meta:
        model = TelegramRecipient
    chat_id = Sequence(lambda n: n+1)
    name = Sequence(lambda n: 'name_%d' % n)
    hook = SubFactory(HookFactory)
    
    
class KikRecipientFactory(DjangoModelFactory):
    class Meta:
        model = KikRecipient
    chat_id = Sequence(lambda n: 'chatId_%d' % n)
    username = Sequence(lambda n: 'username_%d' % n)
    name = Sequence(lambda n: 'name_%d' % n)
    hook = SubFactory(HookFactory)
    
class MessengerRecipientFactory(DjangoModelFactory):
    class Meta:
        model = MessengerRecipient
    chat_id = Sequence(lambda n: 'chatId_%d' % n)
    name = Sequence(lambda n: 'name_%d' % n)
    hook = SubFactory(HookFactory)