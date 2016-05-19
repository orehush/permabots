from rest_framework.views import APIView
from permabots.serializers import KikMessageSerializer
from permabots.models import KikBot, KikUser, KikChat, KikMessage
from rest_framework.response import Response
from rest_framework import status
import logging
from permabots.tasks import handle_message
from datetime import datetime
from permabots import caching
import sys
import traceback

logger = logging.getLogger(__name__)

class OnlyTextMessages(Exception):
    pass


class KikHookView(APIView):
    """
    View for Kik webhook.
    """
    
    def create_user(self, username):
        try:
            user = caching.get_or_set(KikUser, username)
        except KikUser.DoesNotExist:
            user, _ = KikUser.objects.get_or_create(username=username)
        return user
    
    def create_message(self, serializer, bot):
        sender = self.create_user(serializer.data['from'])
        try:
            chat = caching.get_or_set(KikChat, serializer.data['chatId'])
        except KikChat.DoesNotExist:
            chat, _ = KikChat.objects.get_or_create(id=serializer.data['chatId'])
            if 'participants' in serializer.data:
                for participant in serializer.data['participants']:
                    chat.participants.add(self.create_user(participant))                    
        if serializer.data['type'] == 'start-chatting':
            body = "/start"
        elif serializer.data['type'] == 'scan-data':
            body = "/start"
        else:
            body = serializer.data['body']
        message, _ = KikMessage.objects.get_or_create(message_id=serializer.data['id'],
                                                      from_user=sender,
                                                      timestamp=datetime.fromtimestamp(serializer.data['timestamp']),
                                                      chat=chat,
                                                      body=body)
        
        caching.set(message)
        return message
    
    def accepted_types(self, serializer):
        return serializer.data['type'] == 'start-chatting' or serializer.data['type'] == 'text' or serializer.data['type'] == 'scan-data'
    
    def post(self, request, hook_id):
        """
        Process Kik webhook:
            1. Get an enabled Kik bot
            2. Verify Kik signature
            3. Serialize each message
            4. For each message create :class:`KikMessage <permabots.models.kik_api.KikMessage>` and :class:`KikUser <permabots.models.kik_api.KikUser>`
            5. Delay each message processing to a task      
            6. Response provider
        """
        try:
            bot = caching.get_or_set(KikBot, hook_id)
        except KikBot.DoesNotExist:
            logger.warning("Hook id %s not associated to a bot" % hook_id)
            return Response(status=status.HTTP_404_NOT_FOUND)
        signature = request.META.get('HTTP_X_KIK_SIGNATURE')
        if signature:
            signature.encode('utf-8')
        if not bot._bot.verify_signature(signature, request.stream.body):
            logger.debug("Kik Bot data %s not verified %s" % (request.data, signature))
            return Response(status=403)
        logger.debug("Kik Bot data %s verified" % (request.data))
        for kik_message in request.data['messages']:
            serializer = KikMessageSerializer(data=kik_message)   
            logger.debug("Kik message %s serialized" % (kik_message))
            if serializer.is_valid():            
                try:
                    if not self.accepted_types(serializer):
                        raise OnlyTextMessages
                    message = self.create_message(serializer, bot)
                    if bot.enabled:
                        logger.debug("Kik Bot %s attending request %s" % (bot, kik_message))
                        handle_message.delay(message.id, bot.id)
                    else:
                        logger.error("Message %s ignored by disabled bot %s" % (message, bot))
                except OnlyTextMessages:
                    logger.warning("Not text message %s for bot %s" % (kik_message, hook_id))
                    return Response(status=status.HTTP_200_OK)
                except:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)                
                    logger.error("Error processing %s for bot %s" % (kik_message, hook_id))
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                   
            else:
                logger.error("Validation error: %s from kik message %s" % (serializer.errors, kik_message))
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)