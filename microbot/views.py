from rest_framework.views import APIView
from microbot.serializers import UpdateSerializer, BotSerializer, EnvironmentVarSerializer,\
    HandlerSerializer, HookSerializer, RecipientSerializer, AbsParamSerializer, StateSerializer, ChatStateSerializer
from microbot.models import Bot, EnvironmentVar, Handler, Request, Hook, Recipient, UrlParam, HeaderParam, State, ChatState, Chat
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
    
class ObjectBotListView(MicrobotAPIView):
    obj_model = None
    serializer = None
    
    def _user(self, obj):
        return obj.bot.owner
    
    def get_object(self, pk, bot, user):
        try:
            obj = self.obj_model.objects.get(pk=pk, bot=bot)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.obj_model.DoesNotExist:
            raise Http404
        
    def _query(self, bot, obj):
        raise NotImplementedError
    
    def _creator(self, obj, serializer):
        raise NotImplementedError
     
    def get(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        serializer = self.serializer(self._query(bot, obj), many=True)
        return Response(serializer.data)
    
    def post(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            self._creator(obj, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    
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
        target_state = None
        request = None
        if 'target_state' in serializer.data:
            target_state, _ = State.objects.get_or_create(bot=bot,
                                                          name=serializer.data['target_state']['name'])
        if 'request' in serializer.data:
            request = Request.objects.create(url_template=serializer.data['request']['url_template'],
                                             method=serializer.data['request']['method'])

        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        Handler.objects.create(bot=bot,
                               name=serializer.data['name'],
                               pattern=serializer.data['pattern'],
                               response=response,
                               enabled=serializer.data['enabled'],
                               request=request,
                               target_state=target_state)
        
class HandlerDetail(DetailBotAPIView):
    model = Handler
    serializer = HandlerSerializer
    
    
class UrlParameterList(ObjectBotListView):
    serializer = AbsParamSerializer
    obj_model = Handler
    
    def _query(self, bot, obj):
        return obj.request.url_parameters.all()
    
    def _creator(self, obj, serializer):
        UrlParam.objects.create(key=serializer.data['key'],
                                value_template=serializer.data['value_template'],
                                request=obj.request)
        
        
class HeaderParameterList(ObjectBotListView):
    serializer = AbsParamSerializer
    obj_model = Handler
    
    def _query(self, bot, obj):
        return obj.request.header_parameters.all()
    
    def _creator(self, obj, serializer):
        HeaderParam.objects.create(key=serializer.data['key'],
                                   value_template=serializer.data['value_template'],
                                   request=obj.request)
        
class RequestDetailView(MicrobotAPIView):
    model = None
    serializer = None
    
    def get_handler(self, pk, bot, user):
        try:
            handler = Handler.objects.get(pk=pk, bot=bot)
            if handler.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return handler
        except Handler.DoesNotExist:
            raise Http404    
     
    def _user(self, handler):
        return handler.bot.owner        
     
    def get_object(self, pk, handler, user):
        try:
            obj = self.model.objects.get(pk=pk, request=handler.request)
            if self._user(handler) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_pk, handler_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        handler = self.get_handler(handler_pk, bot, request.user)
        obj = self.get_object(pk, handler, request.user)
        serializer = self.serializer(obj)
        return Response(serializer.data)
    
    def put(self, request, bot_pk, handler_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        handler = self.get_handler(handler_pk, bot, request.user)
        obj = self.get_object(pk, handler, request.user)
        serializer = self.serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_pk, handler_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        handler = self.get_handler(handler_pk, bot, request.user)
        obj = self.get_object(pk, handler, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UrlParameterDetail(RequestDetailView):
    model = UrlParam
    serializer = AbsParamSerializer
    
class HeaderParameterDetail(RequestDetailView):
    model = HeaderParam
    serializer = AbsParamSerializer   
    
class FromHandlerViewMixin(object):
    
    def get_handler(self, pk, bot, user):
        try:
            handler = Handler.objects.get(pk=pk, bot=bot)
            if handler.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return handler
        except Hook.DoesNotExist:
            raise Http404  

    
class HookList(ListBotAPIView):
    serializer = HookSerializer
    
    def _query(self, bot):
        return bot.hooks.all()
    
    def _creator(self, bot, serializer):
        
        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        hook = Hook.objects.create(bot=bot,
                                   enabled=serializer.data['enabled'],
                                   response=response,
                                   name=serializer.data['name'])
        for recipient in serializer.data['recipients']:
            Recipient.objects.create(hook=hook,
                                     chat_id=recipient['chat_id'],
                                     name=recipient['name'])
    
    
class HookDetail(DetailBotAPIView):
    model = Hook
    serializer = HookSerializer
    
class RecipientList(ObjectBotListView):
    serializer = RecipientSerializer
    obj_model = Hook
    
    def _query(self, bot, obj):
        return obj.recipients.all()
    
    def _creator(self, obj, serializer):
        Recipient.objects.create(chat_id=serializer.data['chat_id'],
                                 name=serializer.data['name'],
                                 hook=obj)  
    
class RecipientDetail(MicrobotAPIView):
    model = Recipient
    serializer = RecipientSerializer
    
    def get_hook(self, pk, bot, user):
        try:
            hook = Hook.objects.get(pk=pk, bot=bot)
            if hook.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return hook
        except Hook.DoesNotExist:
            raise Http404    
     
    def _user(self, obj):
        return obj.hook.bot.owner
     
    def get_recipient(self, pk, hook, user):
        try:
            obj = self.model.objects.get(pk=pk, hook=hook)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_pk, hook_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        serializer = self.serializer(recipient)
        return Response(serializer.data)
    
    def put(self, request, bot_pk, hook_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        serializer = self.serializer(recipient, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_pk, hook_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        recipient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   
    
    
class StateList(ListBotAPIView):
    serializer = StateSerializer
    
    def _query(self, bot):
        return bot.states.all()

    def _creator(self, bot, serializer):
        State.objects.create(bot=bot,
                             name=serializer.data['name'])
    
class StateDetail(DetailBotAPIView):
    model = State
    serializer = StateSerializer
    
    
class ChatStateList(ListBotAPIView):
    serializer = ChatStateSerializer
    
    def get_state(self, bot, data):
        try:
            state = State.objects.get(bot=bot,
                                      name=data['name'])
            return state
        except State.DoesNotExist:
            raise Http404
        
    def get_chat(self, bot, data):
        try:
            chat = Chat.objects.get(id=data['chat'])
            return chat
        except Chat.DoesNotExist:
            raise Http404            
    
    def _query(self, bot):
        return ChatState.objects.filter(state__bot=bot)

    def _creator(self, bot, serializer):
        state = self.get_state(bot, serializer.data['state'])
        chat = self.get_chat(bot, serializer.data)
        ChatState.objects.create(state=state,
                                 chat=chat)
        
class ChatStateDetail(MicrobotAPIView):
    model = ChatState
    serializer = ChatStateSerializer
    
    def _user(self, obj):
        return obj.state.bot.owner
    
    def get_object(self, pk, bot, user):
        try:
            obj = self.model.objects.get(pk=pk)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            if obj.state.bot != bot:
                raise Http404
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
    
    
class SourceStateList(ObjectBotListView):
    serializer = StateSerializer
    obj_model = Handler
    
    def _query(self, bot, obj):
        return obj.source_states.all()
    
    def _creator(self, obj, serializer):
        state, _ = State.objects.get_or_create(name=serializer.data['name'], bot=obj.bot)
        obj.source_states.add(state)

class SourceStateDetail(RequestDetailView):
    model = State
    serializer = StateSerializer
    
    def get_object(self, pk, handler, user):
        try:
            obj = self.model.objects.get(pk=pk, bot=handler.bot)
            if self._user(handler) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404