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
    serializer_update = ChatStateUpdateSerializer
    
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
        serializer = self.serializer_update(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)