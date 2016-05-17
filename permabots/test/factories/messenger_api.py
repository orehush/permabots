# coding=utf-8
from factory import DjangoModelFactory
from factory.fuzzy import FuzzyText
from permabots.models import MessengerMessage
from django.utils import timezone

class MessengerMessageAPIFactory(DjangoModelFactory):
    class Meta:
        model = MessengerMessage
    sender = FuzzyText()
    recipient = FuzzyText()
    timestamp = timezone.now()
    type = MessengerMessage.MESSAGE
    body = FuzzyText()    