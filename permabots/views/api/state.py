from permabots.serializers import StateSerializer, TelegramChatStateSerializer, TelegramChatStateUpdateSerializer, \
    KikChatStateSerializer, KikChatStateUpdateSerializer, MessengerChatStateSerializer, MessengerChatStateUpdateSerializer
from permabots.models import State, TelegramChatState, TelegramChat, TelegramUser, KikChatState, KikChat, KikUser, MessengerChatState
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from permabots.views.api.base import PermabotsAPIView, ListBotAPIView, DetailBotAPIView


logger = logging.getLogger(__name__)


class StateList(ListBotAPIView):
    serializer = StateSerializer
    
    def _query(self, bot):
        return bot.states.all()

    def _creator(self, bot, serializer):
        return State.objects.create(bot=bot,
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
    
class BaseChatStateList(ListBotAPIView):
    serializer = None
    chat_model = None
    user_model = None
    model = None
    
    def get_state(self, bot, data):
        try:
            state = State.objects.get(bot=bot,
                                      name=data['name'])
            return state
        except State.DoesNotExist:
            raise Http404
        
    def get_chat(self, bot, data):
        try:
            chat = self.chat_model.objects.get(pk=data['chat'])
            return chat
        except self.chat_model.DoesNotExist:
            raise Http404            
        
    def get_user(self, bot, data):
        try:
            chat = self.user_model.objects.get(pk=data['user'])
            return chat
        except self.user_model.DoesNotExist:
            raise Http404         
    
    def _query(self, bot):
        return self.model.objects.filter(state__bot=bot)

    def _creator(self, bot, serializer):
        state = self.get_state(bot, serializer.data['state'])
        chat = self.get_chat(bot, serializer.data)
        user = self.get_user(bot, serializer.data)
        return self.model.objects.create(state=state,
                                         chat=chat,
                                         user=user)
        
    def get(self, request, bot_id, format=None):
        return super(BaseChatStateList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        return super(BaseChatStateList, self).post(request, bot_id, format)
        
class BaseChatStateDetail(PermabotsAPIView):
    model = None
    serializer = None
    serializer_update = None
    
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
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        serializer = self.serializer(obj)
        return Response(serializer.data)

    def put(self, request, bot_id, id, format=None):
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        serializer = self.serializer_update(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, bot_id, id, format=None):
        bot = self.get_bot(bot_id, request.user)
        obj = self.get_object(id, bot, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class TelegramChatStateList(BaseChatStateList):
    serializer = TelegramChatStateSerializer
    chat_model = TelegramChat
    user_model = TelegramUser
    model = TelegramChatState

    def get(self, request, bot_id, format=None):
        """
        Get list of chat state
        ---
        serializer: TelegramChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(TelegramChatStateList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new chat state
        ---
        serializer: TelegramChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(TelegramChatStateList, self).post(request, bot_id, format)
        
class TelegramChatStateDetail(BaseChatStateDetail):
    model = TelegramChatState
    serializer = TelegramChatStateSerializer
    serializer_update = TelegramChatStateUpdateSerializer
        
    def get(self, request, bot_id, id, format=None):
        """
        Get Telegram chat state by id
        ---
        serializer: TelegramChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(TelegramChatStateDetail, self).get(request, bot_id, id, format)

    def put(self, request, bot_id, id, format=None):
        """
        Update existing Telegram chat state
        ---
        serializer: TelegramChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(TelegramChatStateDetail, self).put(request, bot_id, id, format)
    
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing Kik chat state
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(TelegramChatStateDetail, self).delete(request, bot_id, id, format)
    
class KikChatStateList(BaseChatStateList):
    serializer = KikChatStateSerializer
    chat_model = KikChat
    user_model = KikUser
    model = KikChatState
    
    def get(self, request, bot_id, format=None):
        """
        Get list of chat state
        ---
        serializer: KikChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(KikChatStateList, self).get(request, bot_id, format)
     
    def post(self, request, bot_id, format=None):
        """
        Add a new chat state
        ---
        serializer: KikChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(KikChatStateList, self).post(request, bot_id, format)
    
class KikChatStateDetail(BaseChatStateDetail):
    model = KikChatState
    serializer = KikChatStateSerializer
    serializer_update = KikChatStateUpdateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get Kik chat state by id
        ---
        serializer: KikChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(KikChatStateDetail, self).get(request, bot_id, id, format)
 
    def put(self, request, bot_id, id, format=None):
        """
        Update existing Kik chat state
        ---
        serializer: KikChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(KikChatStateDetail, self).put(request, bot_id, id, format)
     
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing Kik chat state
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(KikChatStateDetail, self).delete(request, bot_id, id, format)
    
    
class MessengerChatStateList(BaseChatStateList):
    serializer = MessengerChatStateSerializer
    model = MessengerChatState
    
    def _creator(self, bot, serializer):
        state = self.get_state(bot, serializer.data['state'])
        return self.model.objects.create(state=state,
                                         chat=serializer.data['chat'])
    
    def get(self, request, bot_id, format=None):
        """
        Get list of chat state
        ---
        serializer: MessengerChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(MessengerChatStateList, self).get(request, bot_id, format)
     
    def post(self, request, bot_id, format=None):
        """
        Add a new chat state
        ---
        serializer: MessengerChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(MessengerChatStateList, self).post(request, bot_id, format)
    
    
class MessengerChatStateDetail(BaseChatStateDetail):
    model = MessengerChatState
    serializer = MessengerChatStateSerializer
    serializer_update = MessengerChatStateUpdateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get Messenger chat state by id
        ---
        serializer: MessengerChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(MessengerChatStateDetail, self).get(request, bot_id, id, format)
 
    def put(self, request, bot_id, id, format=None):
        """
        Update existing Messenger chat state
        ---
        serializer: MessengerChatStateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(MessengerChatStateDetail, self).put(request, bot_id, id, format)
     
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing Messenger chat state
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(MessengerChatStateDetail, self).delete(request, bot_id, id, format)    
