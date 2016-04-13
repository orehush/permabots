from rest_framework.views import APIView
from microbot.serializers import UpdateSerializer
from microbot.models import Bot, User, Chat, Message, Update
from rest_framework.response import Response
from rest_framework import status
import logging
from microbot.tasks import handle_update
from datetime import datetime
from microbot import caching
import sys
import traceback


logger = logging.getLogger(__name__)


class TelegramHookView(APIView):
    
    def create_update(self, serializer, bot):
        try:
            user = caching.get_or_set(User, serializer.data['message']['from']['id'])
        except User.DoesNotExist:
            user, _ = User.objects.get_or_create(**serializer.data['message']['from'])
        try:
            chat = caching.get_or_set(Chat, serializer.data['message']['chat']['id'])
        except Chat.DoesNotExist:
            chat, _ = Chat.objects.get_or_create(**serializer.data['message']['chat'])
        
        message, _ = Message.objects.get_or_create(message_id=serializer.data['message']['message_id'],
                                                   from_user=user,
                                                   date=datetime.fromtimestamp(serializer.data['message']['date']),
                                                   chat=chat,
                                                   text=serializer.data['message']['text'])
        update, _ = Update.objects.get_or_create(bot=bot,
                                                 update_id=serializer.data['update_id'],
                                                 message=message)

        return update
    
    def post(self, request, hook_id):
        serializer = UpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                bot = caching.get_or_set(Bot, hook_id)
            except Bot.DoesNotExist:
                logger.warning("Token %s not associated to an bot" % hook_id)
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            try:
                update = self.create_update(serializer, bot)
                if bot.enabled:
                    logger.debug("Bot %s attending request %s" % (bot, request.data))
                    handle_update.delay(update.id, bot.id)
                else:
                    logger.error("Update %s ignored by disabled bot %s" % (update, bot))
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)                
                logger.error("Error processing %s for bot %s" % (request.data, hook_id))
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error("Validation error: %s from message %s" % (serializer.errors, request.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)