from rest_framework.views import APIView
from microbot.serializers import MessageSerializer
from microbot.models import KikBot, KikUser, KikChat, KikMessage
from rest_framework.response import Response
from rest_framework import status
import logging
from microbot.tasks import handle_update
from datetime import datetime
from microbot import caching
import sys
import traceback


logger = logging.getLogger(__name__)

class OnlyTextMessages(Exception):
    pass


class KikHookView(APIView):
    
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
        
        if 'body' not in serializer.data:
            raise OnlyTextMessages
        message, _ = KikMessage.objects.get_or_create(message_id=serializer.data['id'],
                                                      from_user=sender,
                                                      date=datetime.fromtimestamp(serializer.data['message']['date']),
                                                      chat=chat,
                                                      text=serializer.data['body'])
        caching.set(message)
        return message
    
    def post(self, request, hook_id):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                bot = caching.get_or_set(KikBot, hook_id)
            except KikBot.DoesNotExist:
                logger.warning("Hook id %s not associated to a bot" % hook_id)
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            try:
                message = self.create_message(serializer, bot)
                if bot.enabled:
                    logger.debug("Kik Bot %s attending request %s" % (bot, request.data))
                    handle_update.delay(message.id, bot.id)
                else:
                    logger.error("Message %s ignored by disabled bot %s" % (message, bot))
            except OnlyTextMessages:
                logger.warning("Not text message %s for bot %s" % (request.data, hook_id))
                return Response(status=status.HTTP_200_OK)
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)                
                logger.error("Error processing %s for bot %s" % (request.data, hook_id))
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error("Validation error: %s from message %s" % (serializer.errors, request.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)