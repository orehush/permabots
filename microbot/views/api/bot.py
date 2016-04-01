from microbot.serializers import BotSerializer, BotUpdateSerializer
from microbot.views.api.base import MicrobotAPIView
from microbot.models import Bot

from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)


class BotList(MicrobotAPIView):
    
    def get(self, request, format=None):
        bots = Bot.objects.filter(owner=request.user)
        serializer = BotSerializer(bots, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = BotSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Bot.objects.create(owner=request.user,
                                   token=serializer.data['token'],
                                   enabled=serializer.data['enabled'])
            except:
                logger.error("Error trying to create Bot %s" % serializer.data['token'])
                return Response({"error": 'Telegram Error. Check Token or try later.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BotDetail(MicrobotAPIView):
       
    def get(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        serializer = BotSerializer(bot)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        serializer = BotUpdateSerializer(bot, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)