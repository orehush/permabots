# coding=utf-8
from kik.messages import TextMessage, StartChattingMessage
from factory import Sequence, Factory
from factory.fuzzy import FuzzyText
from django.utils import timezone
import uuid

class KikTextMessageLibFactory(Factory):
    class Meta:
        model = TextMessage
    id = uuid.uuid4()
    from_user = FuzzyText()
    timestamp = timezone.now()
    chat_id = Sequence(lambda n: 'chat_id_%d' % n)
    body = FuzzyText()
    
    
class KikStartMessageLibFactory(Factory):
    class Meta:
        model = StartChattingMessage
    id = uuid.uuid4()
    from_user = FuzzyText()
    timestamp = timezone.now()
    chat_id = Sequence(lambda n: 'chat_id_%d' % n)
