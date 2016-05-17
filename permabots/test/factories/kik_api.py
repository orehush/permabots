# coding=utf-8
from factory import DjangoModelFactory, Sequence, SubFactory
from factory.fuzzy import FuzzyText
from permabots.models import KikChat, KikUser, KikMessage
from django.utils import timezone

class KikUserAPIFactory(DjangoModelFactory):
    class Meta:
        model = KikUser
    first_name = Sequence(lambda n: 'first_name_%d' % n)
    last_name = Sequence(lambda n: 'last_name_%d' % n)
    username = FuzzyText()

class KikChatAPIFactory(DjangoModelFactory):
    class Meta:
        model = KikChat
    id = Sequence(lambda n: 'id_%d' % n)

class KikMessageAPIFactory(DjangoModelFactory):
    class Meta:
        model = KikMessage
    message_id = Sequence(lambda n: n+1)
    from_user = SubFactory(KikUserAPIFactory)
    timestamp = timezone.now()
    chat = SubFactory(KikChatAPIFactory)
    body = FuzzyText()