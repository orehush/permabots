from rest_framework.views import APIView
from microbot.serializers import UpdateSerializer, BotSerializer, EnvironmentVarSerializer
from microbot.models import Bot, EnvironmentVar
from rest_framework.response import Response
from rest_framework import status
from telegram import Update
import logging
import sys
import traceback
from microbot.tasks import handle_update
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http.response import Http404
from rest_framework import exceptions

logger = logging.getLogger(__name__)

class WebhookView(APIView):
    
    def post(self, request, token):
        serializer = UpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                bot = Bot.objects.get(token=token, enabled=True)
                logger.debug("Bot %s attending request %s" % (bot, request.data))
                handle_update.delay(Update.de_json(request.data).update_id, bot.id)
            except Bot.DoesNotExist:
                logger.warning("Token %s not associated to an enabled bot" % token)
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                logger.error("Error processing %s for token %s" % (request.data, token))
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error("Validation error: %s from message %s" % (serializer.errors, request.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BotList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        bots = Bot.objects.filter(owner=request.user)
        serializer = BotSerializer(bots, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = BotSerializer(data=request.data)
        if serializer.is_valid():
            Bot.objects.create(owner=request.user,
                               token=serializer.data['token'],
                               enabled=serializer.data['enabled'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BotDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, pk, user):
        try:
            bot = Bot.objects.get(pk=pk)
            if bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return bot
        except Bot.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        bot = self.get_object(pk, request.user)
        serializer = BotSerializer(bot)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        bot = self.get_object(pk, request.user)
        serializer = BotSerializer(bot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bot = self.get_object(pk, request.user)
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnvironmentVarList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, pk, user):
        try:
            bot = Bot.objects.get(pk=pk)
            if bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return bot
        except Bot.DoesNotExist:
            raise Http404    
    
    def get(self, request, bot_pk, format=None):
        bot = self.get_object(bot_pk, request.user)
        serializer = EnvironmentVarSerializer(bot.env_vars.all(), many=True)
        return Response(serializer.data)
    
    def post(self, request, bot_pk, format=None):
        bot = self.get_object(bot_pk, request.user)
        serializer = EnvironmentVarSerializer(data=request.data)
        if serializer.is_valid():
            EnvironmentVar.objects.create(bot=bot,
                                          key=serializer.data['key'],
                                          value=serializer.data['value'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EnvironmentVarDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_bot(self, pk, user):
        try:
            bot = Bot.objects.get(pk=pk)
            if bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return bot
        except Bot.DoesNotExist:
            raise Http404    
        
    def get_object(self, pk, bot, user):
        try:
            env_var = EnvironmentVar.objects.get(pk=pk, bot=bot)
            if env_var.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return env_var
        except EnvironmentVar.DoesNotExist:
            raise Http404
        
    def get(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        env_var = self.get_object(pk, bot, request.user)
        serializer = EnvironmentVarSerializer(env_var)
        return Response(serializer.data)

    def put(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        env_var = self.get_object(pk, bot, request.user)
        serializer = EnvironmentVarSerializer(env_var, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        env_var = self.get_object(pk, bot, request.user)
        env_var.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
