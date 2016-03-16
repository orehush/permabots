from rest_framework.views import APIView
from microbot.serializers import UpdateSerializer, BotSerializer, EnvironmentVarSerializer,\
    HandlerSerializer, HookSerializer
from microbot.models import Bot, EnvironmentVar, Handler, Request, Hook, Recipient
from microbot.models import Response as handlerResponse
from rest_framework.response import Response
from rest_framework import status
from telegram import Update
import logging
import sys
import traceback
from microbot.tasks import handle_update, handle_hook
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http.response import Http404
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _

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
    
class HookView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, key):
        try:
            hook = Hook.objects.get(key=key, enabled=True, bot__enabled=True)
        except Hook.DoesNotExist:
            msg = _("Key %s not associated to an enabled hook or bot") % key
            logger.warning(msg)
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        if hook.bot.owner != request.user:
                raise exceptions.AuthenticationFailed()
        try:
            logger.debug("Hook %s attending request %s" % (hook, request.data))
            handle_hook.delay(hook.id, request.data)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            msg = _("Error processing %s for key %s") % (request.data, key)
            logger.error(msg)
            return Response(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_200_OK)
    
class MicrobotAPIView(APIView):
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
            
class BotList(MicrobotAPIView):
    
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

class BotDetail(MicrobotAPIView):
       
    def get(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        serializer = BotSerializer(bot)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        serializer = BotSerializer(bot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bot = self.get_bot(pk, request.user)
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ListBotAPIView(MicrobotAPIView):
    serializer = None
    
    def _query(self, bot):
        raise NotImplemented
    
    def _creator(self, bot, serializer):
        raise NotImplemented
    
    def get(self, request, bot_pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        serializer = self.serializer(self._query(bot), many=True)
        return Response(serializer.data)
    
    def post(self, request, bot_pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            self._creator(bot, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
class DetailBotAPIView(MicrobotAPIView):
    model = None
    serializer = None
    
    def _user(self, obj):
        return obj.bot.owner
    
    def get_object(self, pk, bot, user):
        try:
            obj = self.model.objects.get(pk=pk, bot=bot)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
        
    def get(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        serializer = self.serializer(obj)
        return Response(serializer.data)

    def put(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        serializer = self.serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
    
    
class EnvironmentVarList(ListBotAPIView):
    serializer = EnvironmentVarSerializer
    
    def _query(self, bot):
        return bot.env_vars.all()

    def _creator(self, bot, serializer):
        EnvironmentVar.objects.create(bot=bot,
                                      key=serializer.data['key'],
                                      value=serializer.data['value'])
    
class EnvironmentVarDetail(DetailBotAPIView):
    model = EnvironmentVar
    serializer = EnvironmentVarSerializer    

    
class HandlerList(ListBotAPIView):
    serializer = HandlerSerializer
    
    def _query(self, bot):
        return bot.handlers.all()
    
    def _creator(self, bot, serializer):
        request = Request.objects.create(url_template=serializer.data['request']['url_template'],
                                         method=serializer.data['request']['method'])
        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        Handler.objects.create(bot=bot,
                               pattern=serializer.data['pattern'],
                               response=response,
                               enabled=serializer.data['enabled'],
                               request=request)
        
class HandlerDetail(DetailBotAPIView):
    model = Handler
    serializer = HandlerSerializer
    
class HookList(ListBotAPIView):
    serializer = HookSerializer
    
    def _query(self, bot):
        return bot.hooks.all()
    
    def _creator(self, bot, serializer):
        
        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        hook = Hook.objects.create(bot=bot,
                                   enabled=serializer.data['enabled'],
                                   response=response)
        for recipient in serializer.data['recipients']:
            Recipient.objects.create(hook=hook,
                                     id=recipient['id'])
    
    
class HookDetail(DetailBotAPIView):
    model = Hook
    serializer = HookSerializer
