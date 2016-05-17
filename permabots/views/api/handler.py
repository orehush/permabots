from permabots.serializers import HandlerSerializer, AbsParamSerializer, StateSerializer, HandlerUpdateSerializer
from permabots.models import Handler, Request, Hook, UrlParam, HeaderParam, State
from permabots.models import Response as handlerResponse
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from permabots.views.api.base import ListBotAPIView, PermabotsAPIView, DetailBotAPIView, ObjectBotListView
import json

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
            data = serializer.data['request'].get('data', None)
            if data:
                data = json.dumps(data)
            request = Request.objects.create(url_template=serializer.data['request']['url_template'],
                                             method=serializer.data['request']['method'],
                                             data=data)

        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        return Handler.objects.create(bot=bot,
                                      name=serializer.data['name'],
                                      pattern=serializer.data['pattern'],
                                      priority=serializer.data.get('priority', 0),
                                      response=response,
                                      enabled=serializer.data['enabled'],
                                      request=request,
                                      target_state=target_state)
        
    def get(self, request, bot_id, format=None):
        """
        Get list of handlers
        ---
        serializer: HandlerSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HandlerList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new handler
        ---
        serializer: HandlerSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(HandlerList, self).post(request, bot_id, format)
        
class HandlerDetail(DetailBotAPIView):
    model = Handler
    serializer = HandlerSerializer
    serializer_update = HandlerUpdateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get handler by id
        ---
        serializer: HandlerSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(HandlerDetail, self).get(request, bot_id, id, format)
    
    def put(self, request, bot_id, id, format=None):
        """
        Update existing handler
        ---
        serializer: HandlerUpdateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(HandlerDetail, self).put(request, bot_id, id, format)
        
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing handler
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HandlerDetail, self).delete(request, bot_id, id, format)
    
    
class UrlParameterList(ObjectBotListView):
    serializer = AbsParamSerializer
    obj_model = Handler
    
    def _query(self, bot, obj):
        return obj.request.url_parameters.all()
    
    def _creator(self, obj, serializer):
        return UrlParam.objects.create(key=serializer.data['key'],
                                       value_template=serializer.data['value_template'],
                                       request=obj.request)
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of url parameters of a handler
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(UrlParameterList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new url parameter to a handler
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(UrlParameterList, self).post(request, bot_id, id, format)
        
        
class HeaderParameterList(ObjectBotListView):
    serializer = AbsParamSerializer
    obj_model = Handler
    
    def _query(self, bot, obj):
        return obj.request.header_parameters.all()
    
    def _creator(self, obj, serializer):
        return HeaderParam.objects.create(key=serializer.data['key'],
                                          value_template=serializer.data['value_template'],
                                          request=obj.request)
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of header parameters of a handler
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HeaderParameterList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new header parameter to a handler
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(HeaderParameterList, self).post(request, bot_id, id, format)
        
class RequestDetailView(PermabotsAPIView):
    model = None
    serializer = None
    
    def get_handler(self, id, bot, user):
        try:
            handler = Handler.objects.get(id=id, bot=bot)
            if handler.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return handler
        except Handler.DoesNotExist:
            raise Http404    
     
    def _user(self, handler):
        return handler.bot.owner        
     
    def get_object(self, id, handler, user):
        try:
            obj = self.model.objects.get(id=id, request=handler.request)
            if self._user(handler) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_id, handler_id, id, format=None):
        bot = self.get_bot(bot_id, request.user)
        handler = self.get_handler(handler_id, bot, request.user)
        obj = self.get_object(id, handler, request.user)
        serializer = self.serializer(obj)
        return Response(serializer.data)
    
    def put(self, request, bot_id, handler_id, id, format=None):
        bot = self.get_bot(bot_id, request.user)
        handler = self.get_handler(handler_id, bot, request.user)
        obj = self.get_object(id, handler, request.user)
        serializer = self.serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(self.serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_id, handler_id, id, format=None):
        bot = self.get_bot(bot_id, request.user)
        handler = self.get_handler(handler_id, bot, request.user)
        obj = self.get_object(id, handler, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UrlParameterDetail(RequestDetailView):
    model = UrlParam
    serializer = AbsParamSerializer
    
    def get(self, request, bot_id, handler_id, id, format=None):
        """
        Get url parameter by id
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(UrlParameterDetail, self).get(request, bot_id, handler_id, id, format)
    
    def put(self, request, bot_id, handler_id, id, format=None):
        """
        Update an existing url parameter
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(UrlParameterDetail, self).put(request, bot_id, handler_id, id, format)
    
    def delete(self, request, bot_id, handler_id, id, format=None):
        """
        Delete an existing url parameter
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(UrlParameterDetail, self).delete(request, bot_id, handler_id, id, format)
    
class HeaderParameterDetail(RequestDetailView):
    model = HeaderParam
    serializer = AbsParamSerializer
    
    def get(self, request, bot_id, handler_id, id, format=None):
        """
        Get header parameter by id
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HeaderParameterDetail, self).get(request, bot_id, handler_id, id, format)
    
    def put(self, request, bot_id, handler_id, id, format=None):
        """
        Update an existing header parameter
        ---
        serializer: AbsParamSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(HeaderParameterDetail, self).put(request, bot_id, handler_id, id, format)
    
    def delete(self, request, bot_id, handler_id, id, format=None):
        """
        Delete an existing header parameter
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HeaderParameterDetail, self).delete(request, bot_id, handler_id, id, format)
    
class FromHandlerViewMixin(object):
    
    def get_handler(self, id, bot, user):
        try:
            handler = Handler.objects.get(id=id, bot=bot)
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
        return state
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of source state of a handler
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(SourceStateList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new source state to a handler
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(SourceStateList, self).post(request, bot_id, id, format)

class SourceStateDetail(RequestDetailView):
    model = State
    serializer = StateSerializer
    
    def get_object(self, id, handler, user):
        try:
            obj = self.model.objects.get(id=id, bot=handler.bot)
            if self._user(handler) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
        
    def get(self, request, bot_id, handler_id, id, format=None):
        """
        Get source state by id
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(SourceStateDetail, self).get(request, bot_id, handler_id, id, format)
    
    def put(self, request, bot_id, handler_id, id, format=None):
        """
        Update an existing source state
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(SourceStateDetail, self).put(request, bot_id, handler_id, id, format)
    
    def delete(self, request, bot_id, handler_id, id, format=None):
        """
        Delete an existing source state
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(SourceStateDetail, self).delete(request, bot_id, handler_id, id, format)