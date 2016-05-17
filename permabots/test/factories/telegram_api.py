# coding=utf-8
from factory import DjangoModelFactory, Sequence, SubFactory
from factory.fuzzy import FuzzyText
from permabots.models import TelegramUser, TelegramChat, TelegramMessage, TelegramUpdate
from django.utils import timezone

class TelegramUserAPIFactory(DjangoModelFactory):
    class Meta:
        model = TelegramUser
    id = Sequence(lambda n: n+1)
    first_name = Sequence(lambda n: 'first_name_%d' % n)
    last_name = Sequence(lambda n: 'last_name_%d' % n)
    username = Sequence(lambda n: 'username_%d' % n)

class TelegramChatAPIFactory(DjangoModelFactory):
    class Meta:
        model = TelegramChat
    id = Sequence(lambda n: n+1)
    type = "private"
    title = Sequence(lambda n: 'title_%d' % n)
    username = Sequence(lambda n: 'username_%d' % n)
    first_name = Sequence(lambda n: 'first_name_%d' % n)
    last_name = Sequence(lambda n: 'last_name_%d' % n)

class TelegramMessageAPIFactory(DjangoModelFactory):
    class Meta:
        model = TelegramMessage
    message_id = Sequence(lambda n: n+1)
    from_user = SubFactory(TelegramUserAPIFactory)
    date = timezone.now()
    chat = SubFactory(TelegramChatAPIFactory)
    text = FuzzyText()    

class TelegramUpdateAPIFactory(DjangoModelFactory):
    class Meta:
        model = TelegramUpdate
    update_id = Sequence(lambda n: n+1)
    message = SubFactory(TelegramMessageAPIFactory)
