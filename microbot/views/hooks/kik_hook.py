from rest_framework.views import APIView
from microbot.serializers import KikMessageSerializer
from microbot.models import KikBot, KikUser, KikChat, KikMessage
from rest_framework.response import Response
from rest_framework import status
import logging
from microbot.tasks import handle_message
from datetime import datetime
from microbot import caching
import sys
import traceback
import json

logger = logging.getLogger(__name__)

class OnlyTextMessages(Exception):
    pass


class KikHookView(APIView):
    
    def create_user(self, username):
        # TODO: caching without id. Use pk
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

        message, _ = KikMessage.objects.get_or_create(message_id=serializer.data['id'],
                                                      from_user=sender,
                                                      timestamp=datetime.fromtimestamp(serializer.data['timestamp']),
                                                      chat=chat,
                                                      body=serializer.data['body'])
        caching.set(message)
        return message
    
    def post(self, request, hook_id):
        try:
            bot = caching.get_or_set(KikBot, hook_id)
        except KikBot.DoesNotExist:
            logger.warning("Hook id %s not associated to a bot" % hook_id)
            return Response(status=status.HTTP_404_NOT_FOUND)
        signature = request.META.get('X-Kik-Signature')
        logger.debug("Signature: %s for data %s" % (signature, request.data))
        if signature:
            signature.encode('utf-8')
        if not bot._bot.verify_signature(signature, json.dumps(request.data)):
            return Response(status=403)
        logger.debug("Kik Bot data %s verified" % (request.data))
        for kik_message in request.data['messages']:
            serializer = KikMessageSerializer(data=kik_message)   
            logger.debug("Kik message %s serializer %s" % (kik_message))
            if serializer.is_valid():            
                try:
                    if 'body' not in serializer.data:
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