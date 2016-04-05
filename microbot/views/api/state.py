from microbot.serializers import StateSerializer, ChatStateSerializer, ChatStateUpdateSerializer
from microbot.models import State, ChatState, Chat
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from microbot.views.api.base import MicrobotAPIView, ListBotAPIView, DetailBotAPIView


logger = logging.getLogger(__name__)


class StateList(ListBotAPIView):
    serializer = StateSerializer
    
    def _query(self, bot):
        return bot.states.all()

    def _creator(self, bot, serializer):
        State.objects.create(bot=bot,
                             name=serializer.data['name'])
        
    def get(self, request, bot_id, format=None):
        """
        Get list of states
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(StateList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new state
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(StateList, self).post(request, bot_id, format)
    
class StateDetail(DetailBotAPIView):
    model = State
    serializer = StateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get state by id
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(StateDetail, self).get(request, bot_id, id, format)
    
    def put(self, request, bot_id, id, format=None):
        """
        Update existing state
        ---
        serializer: StateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(StateDetail, self).put(request, bot_id, id, format)
        
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing state
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(StateDetail, self).delete(request, bot_id, id, format)
    
    
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
        
    def get(self, request, bot_id, format=None):
        """
        Get list of chat state
        ---
        serializer: ChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(ChatStateList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new chat state
        ---
        serializer: ChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(ChatStateList, self).post(request, bot_id, format)
        
class ChatStateDetail(MicrobotAPIView):
    model = ChatState
    serializer = ChatStateSerializer
    serializer_update = ChatStateUpdateSerializer
    
    def _user(self, obj):
        return obj.state.bot.owner
    
    def get_object(self, id, bot, user):
        try:
            obj = self.model.objects.get(id=id)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            if obj.state.bot != bot:
                raise Http404
            return obj
        except self.model.DoesNotExist:
            raise Http404
        
    def get(self, request, bot_id, id, format=None):
        """
        Get chat state by id
        ---
        serializer: ChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        serializer = self.serializer(obj)
        return Response(serializer.data)

    def put(self, request, bot_id, id, format=None):
        """
        Update existing chat state
        ---
        serializer: ChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        serializer = self.serializer_update(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing chat state
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)