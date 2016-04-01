from microbot.serializers import HandlerSerializer, AbsParamSerializer, StateSerializer, HandlerUpdateSerializer
from microbot.models import Handler, Request, Hook, UrlParam, HeaderParam, State
from microbot.models import Response as handlerResponse
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from microbot.views.api.base import ListBotAPIView, MicrobotAPIView, DetailBotAPIView, ObjectBotListView

logger = logging.getLogger(__name__)


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
    serializer_update = HandlerUpdateSerializer
    
    
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