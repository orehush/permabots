from rest_framework.views import APIView
from permabots.models import MessengerBot, MessengerMessage
from rest_framework.response import Response
from rest_framework import status
import logging
from permabots.tasks import handle_messenger_message
from datetime import datetime
from permabots import caching
import sys
import traceback
from time import mktime
from six import iteritems

logger = logging.getLogger(__name__)

class OnlyTextMessages(Exception):
    pass


class Resource(object):
    def to_json(self):
        output_json = {}
        for obj_key, json_key in iteritems(self.property_mapping()):
            attr = getattr(self, obj_key)
            if attr is not None:
                output_json[json_key] = attr
        return output_json
    
    @classmethod
    def from_json(cls, json):
        mapping = {v: k for k, v in iteritems(cls.property_mapping())}
        return cls(**{mapping[key]: value for key, value in iteritems(json) if key in mapping})
    
    @classmethod
    def property_mapping(cls):
        """
        A map of property name to json key name for properties that can be simply serialized to/from json
        (no objects, etc.)
        """
        raise NotImplementedError('Resource objects must define a property_mapping')

class MessengerTextMessage(Resource):
    
    def __init__(self, mid, seq, text):
        self.mid = mid
        self.seq = seq
        self.text = text
    
    @classmethod
    def property_mapping(cls):
        return {
            'mid': 'mid',
            'seq': 'seq',
            'text': 'text'
        }
        
class MessengerPostbackMessage(Resource):
    
    def __init__(self, payload):
        self.payload = payload
        
    @classmethod
    def property_mapping(cls):
        return {
            'payload': 'payload'
        }
        
class MessengerMessaging(Resource):
    
    def __init__(self, sender=None, recipient=None, timestamp=None, type=None, message=None):
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp
        self.type = type
        self.message = message
        
    @property
    def is_message(self):
        return self.type == 'message'
    
    @property
    def is_postback(self):
        return self.type == 'postback'
    
    @property
    def is_delivery(self):
        return self.type == 'delivery'
    
    @classmethod
    def property_mapping(cls):
        return {}
    
    def to_json(self):
        output_json = super(MessengerMessaging, self).to_json()
        output_json['sender'] = {'id': self.sender}
        output_json['recipient'] = {'id': self.recipient}
        output_json['timestamp'] = int(mktime(self.timestamp.timetuple()))
        output_json[self.type] = self.message.to_json()
        return output_json
    
    @classmethod
    def from_json(cls, json):
        message = super(MessengerMessaging, cls).from_json(json)

        if 'timestamp' in json:
            message.timestamp = datetime.fromtimestamp(json['timestamp']/1000.)
        if 'sender' in json:
            message.sender = json['sender']['id']
        if 'recipient' in json:
            message.recipient = json['recipient']['id']
        if 'message' in json:
            message.type = 'message'
            message.message = MessengerTextMessage.from_json(json['message'])
        elif 'postback' in json:
            message.type = 'postback'
            message.message = MessengerPostbackMessage.from_json(json['postback'])
        else:
            message.type = 'delivery'

        return message
    
class MessengerEntry(Resource):
    
    def __init__(self, page_id, time=None, messaging=None):
        self.page_id = page_id
        self.time = time
        self.messaging = messaging
        
    @classmethod
    def property_mapping(cls):
        return {
            'page_id': 'id',
        }   
    
    def to_json(self):
        output_json = super(MessengerEntry, self).to_json()
        output_json['time'] = int(mktime(self.time.timetuple()))
        output_json['messaging'] = [message.to_json() for message in self.messaging]
        return output_json
    
    @classmethod
    def from_json(cls, json):
        entry = super(MessengerEntry, cls).from_json(json)

        if 'time' in json:
            entry.time = datetime.fromtimestamp(json['time']/1000.)
        if 'messaging' in json:
            entry.messaging = [MessengerMessaging.from_json(msg) for msg in json['messaging']]

        return entry
    
class Webhook(Resource):
    
    def __init__(self, object, entries=None):
        self.entries = entries
    
    def to_json(self):
        output_json = {'object': "page",
                       'entry': [entry.to_json() for entry in self.entries]}
        return output_json
    
    @classmethod
    def from_json(cls, json):
        webhook = super(Webhook, cls).from_json(json)

        if 'entry' in json:
            webhook.entries = [MessengerEntry.from_json(entry) for entry in json['entry']]

        return webhook
    
    @classmethod
    def property_mapping(cls):
        return {
            'object': 'object',
        }   


class MessengerHookView(APIView):
    """
    View for Facebook Messenger webhook
    """
    
    def get(self, request, hook_id):
        """
        Verify token when configuring webhook from facebook dev.
        
        MessengerBot.id is used for verification
        """
        try:
            bot = caching.get_or_set(MessengerBot, hook_id)
        except MessengerBot.DoesNotExist:
            logger.warning("Hook id %s not associated to a bot" % hook_id)
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.query_params.get('hub.verify_token') == str(bot.id):
            return Response(int(request.query_params.get('hub.challenge')))
        return Response('Error, wrong validation token')
    
    def create_message(self, webhook_message, bot):
        if webhook_message.is_message:
            type = MessengerMessage.MESSAGE
            text = webhook_message.message.text
            postback = None
        else:
            type = MessengerMessage.POSTBACK
            text = None
            postback = webhook_message.message.payload            
        
        message, _ = MessengerMessage.objects.get_or_create(bot=bot,
                                                            sender=webhook_message.sender,
                                                            recipient=webhook_message.recipient,
                                                            timestamp=webhook_message.timestamp,
                                                            type=type,
                                                            text=text,
                                                            postback=postback)
        
        caching.set(message)
        return message

    def post(self, request, hook_id):
        """
        Process Messenger webhook.
            1. Get an enabled Messenger bot
            3. For each message serialize
            4. For each message create :class:`MessengerMessage <permabots.models.messenger_api.MessengerMessage>`
            5. Delay processing of each message to a task      
            6. Response provider
        """
        try:
            bot = caching.get_or_set(MessengerBot, hook_id)
        except MessengerBot.DoesNotExist:
            logger.warning("Hook id %s not associated to a bot" % hook_id)
            return Response(status=status.HTTP_404_NOT_FOUND)
        logger.debug("Messenger Bot %s attending request %s" % (bot, request.data))
        webhook = Webhook.from_json(request.data)
        for webhook_entry in webhook.entries:
            for webhook_message in webhook_entry.messaging:
                try:
                    if webhook_message.is_delivery:
                        raise OnlyTextMessages
                    message = self.create_message(webhook_message, bot)
                    if bot.enabled:
                        logger.debug("Messenger Bot %s attending request %s" % (bot, message))
                        handle_messenger_message.delay(message.id, bot.id)
                    else:
                        logger.error("Message %s ignored by disabled bot %s" % (message, bot))
                except OnlyTextMessages:
                    logger.warning("Not text message %s for bot %s" % (message, hook_id))
                except:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)                
                    logger.error("Error processing %s for bot %s" % (webhook_message, hook_id))
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)        