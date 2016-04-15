from microbot.serializers import BotSerializer, BotUpdateSerializer, TelegramBotSerializer, TelegramBotUpdateSerializer
from microbot.views.api.base import MicrobotAPIView
from microbot.models import Bot, TelegramBot

from rest_framework.response import Response
from rest_framework import status
from microbot.views.api.base import ListBotAPIView, DetailBotAPIView
import logging

logger = logging.getLogger(__name__)


class BotList(MicrobotAPIView):    
    
    def get(self, request, format=None):
        """
        Get list of bots
        ---
        serializer: BotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bots = Bot.objects.filter(owner=request.user)
        serializer = BotSerializer(bots, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        """
        Add a new bot
        ---
        serializer: BotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        serializer = BotSerializer(data=request.data)
        if serializer.is_valid():
            bot = Bot.objects.create(owner=request.user,
                                     name=serializer.data['name'])
            return Response(BotSerializer(bot).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BotDetail(MicrobotAPIView):
       
    def get(self, request, id, format=None):
        """
        Get bot by id
        ---
        serializer: BotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(id, request.user)
        serializer = BotSerializer(bot)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """
        Update an existing bot
        ---
        serializer: BotUpdateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        bot = self.get_bot(id, request.user)
        serializer = BotUpdateSerializer(bot, data=request.data)
        if serializer.is_valid():
            try:
                bot = serializer.save()
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(BotSerializer(bot).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        Delete an existing bot
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(id, request.user)
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class TelegramBotList(ListBotAPIView):
    serializer = TelegramBotSerializer
    many = False
    
    def _query(self, bot):
        return bot.telegram_bot

    def _creator(self, bot, serializer):
        try:
            telegram_bot = TelegramBot.objects.create(token=serializer.data['token'],
                                                      enabled=serializer.data['enabled'])
        except:
            logger.error("Error trying to create Bot %s" % serializer.data['token'])
            raise
        else:
            bot.telegram_bot = telegram_bot
            bot.save()
            return telegram_bot
        
    def get(self, request, bot_id, format=None):
        """
        Get list of Telegram bots
        ---
        serializer: TelegramBotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(TelegramBotList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add TelegramBot
        ---
        serializer: TelegramBotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        try:
            return super(TelegramBotList, self).post(request, bot_id, format)
        except:
            return Response({"error": 'Telegram Error. Check Token or try later.'}, status=status.HTTP_400_BAD_REQUEST)
    
class TelegramBotDetail(DetailBotAPIView):
    model = TelegramBot
    serializer = TelegramBotSerializer
    serializer_update = TelegramBotUpdateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get TelegramBot by id
        ---
        serializer: TelegramBotSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(TelegramBotDetail, self).get(request, bot_id, id, format)
    
    def put(self, request, bot_id, id, format=None):
        """
        Update existing TelegramBot
        ---
        serializer: TelegramBotUpdateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(TelegramBotDetail, self).put(request, bot_id, id, format)
        
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing Telegram Bot
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(TelegramBotDetail, self).delete(request, bot_id, id, format)