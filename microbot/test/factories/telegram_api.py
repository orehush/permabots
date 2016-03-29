# coding=utf-8
from factory import DjangoModelFactory, Sequence, SubFactory
from factory.fuzzy import FuzzyText
from microbot.models import User, Chat, Message, Update
from django.utils import timezone

class UserAPIFactory(DjangoModelFactory):
    class Meta:
        model = User
    id = Sequence(lambda n: n+1)
    first_name = Sequence(lambda n: 'first_name_%d' % n)
    last_name = Sequence(lambda n: 'last_name_%d' % n)
    username = Sequence(lambda n: 'username_%d' % n)

class ChatAPIFactory(DjangoModelFactory):
    class Meta:
        model = Chat
    id = Sequence(lambda n: n+1)
    type = "private"
    title = Sequence(lambda n: 'title_%d' % n)
    username = Sequence(lambda n: 'username_%d' % n)
    first_name = Sequence(lambda n: 'first_name_%d' % n)
    last_name = Sequence(lambda n: 'last_name_%d' % n)

class MessageAPIFactory(DjangoModelFactory):
    class Meta:
        model = Message
    message_id = Sequence(lambda n: n+1)
    from_user = SubFactory(UserAPIFactory)
    date = timezone.now()
    chat = SubFactory(ChatAPIFactory)
    text = FuzzyText()    

class UpdateAPIFactory(DjangoModelFactory):
    class Meta:
        model = Update
    update_id = Sequence(lambda n: n+1)
    message = SubFactory(MessageAPIFactory)
