# coding=utf-8
from factory import Factory, SubFactory
from factory.fuzzy import FuzzyText, FuzzyInteger
from django.utils import timezone
from permabots.views.hooks import messenger_hook


class MessengerTextMessageFactory(Factory):
    class Meta:
        model = messenger_hook.MessengerTextMessage
    mid = FuzzyText()
    seq = FuzzyInteger(10000000)
    text = FuzzyText()
    
class MessengerPostBackMessageFactory(Factory):
    class Meta:
        model = messenger_hook.MessengerPostbackMessage
    payload = FuzzyText()
    
class MessengerMessagingFactory(Factory):
    class Meta:
        model = messenger_hook.MessengerMessaging
    sender = FuzzyText()
    recipient = FuzzyText()
    timestamp = timezone.now()
    type = "message"
    message = SubFactory(MessengerTextMessageFactory)

class MessengerEntryFactory(Factory):
    class Meta:
        model = messenger_hook.MessengerEntry
    page_id = FuzzyText()
    time = timezone.now()
    messaging = []
    
class MessengerWebhookFactory(Factory):
    class Meta:
        model = messenger_hook.Webhook
    object = "page"
    entries = []