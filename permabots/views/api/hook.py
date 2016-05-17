from permabots.serializers import HookSerializer, TelegramRecipientSerializer, HookUpdateSerializer, KikRecipientSerializer, MessengerRecipientSerializer
from permabots.models import Hook, TelegramRecipient, KikRecipient, MessengerRecipient
from permabots.models import Response as handlerResponse
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from permabots.views.api.base import PermabotsAPIView, ListBotAPIView, DetailBotAPIView, ObjectBotListView


logger = logging.getLogger(__name__)


class HookList(ListBotAPIView):
    serializer = HookSerializer
    
    def _query(self, bot):
        return bot.hooks.all()
    
    def _creator(self, bot, serializer):
        
        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        return Hook.objects.create(bot=bot,
                                   enabled=serializer.data['enabled'],
                                   response=response,
                                   name=serializer.data['name'])
        
    def get(self, request, bot_id, format=None):
        """
        Get list of hooks
        ---
        serializer: HookSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HookList, self).get(request, bot_id, format)
    
    def post(self, request, bot_id, format=None):
        """
        Add a new hook
        ---
        serializer: HookSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(HookList, self).post(request, bot_id, format)
    
    
class HookDetail(DetailBotAPIView):
    model = Hook
    serializer = HookSerializer
    serializer_update = HookUpdateSerializer
    
    def get(self, request, bot_id, id, format=None):
        """
        Get hook by id
        ---
        serializer: HookSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(HookDetail, self).get(request, bot_id, id, format)
    
    def put(self, request, bot_id, id, format=None):
        """
        Update existing hook
        ---
        serializer: HookUpdateSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """      
        return super(HookDetail, self).put(request, bot_id, id, format)
        
    def delete(self, request, bot_id, id, format=None):
        """
        Delete existing hook
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HookDetail, self).delete(request, bot_id, id, format)
    
class TelegramRecipientList(ObjectBotListView):
    serializer = TelegramRecipientSerializer
    obj_model = Hook
    
    def _query(self, bot, obj):
        return obj.telegram_recipients.all()
    
    def _creator(self, obj, serializer):
        return TelegramRecipient.objects.create(chat_id=serializer.data['chat_id'],
                                                name=serializer.data['name'],
                                                hook=obj)
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of telegram recipients of a hook
        ---
        serializer: TelegramRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(TelegramRecipientList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new telegram recipient to a handler
        ---
        serializer: TelegramRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(TelegramRecipientList, self).post(request, bot_id, id, format)
    
class TelegramRecipientDetail(PermabotsAPIView):
    model = TelegramRecipient
    serializer = TelegramRecipientSerializer
    
    def get_hook(self, id, bot, user):
        try:
            hook = Hook.objects.get(id=id, bot=bot)
            if hook.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return hook
        except Hook.DoesNotExist:
            raise Http404    
     
    def _user(self, obj):
        return obj.hook.bot.owner
     
    def get_recipient(self, id, hook, user):
        try:
            obj = self.model.objects.get(id=id, hook=hook)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_id, hook_id, id, format=None):
        """
        Get recipient by id
        ---
        serializer: TelegramRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient)
        return Response(serializer.data)
    
    def put(self, request, bot_id, hook_id, id, format=None):
        """
        Update existing telegram recipient
        ---
        serializer: TelegramRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_id, hook_id, id, format=None):
        """
        Delete an existing telegram recipient
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        recipient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   
    
    
class KikRecipientList(ObjectBotListView):
    serializer = KikRecipientSerializer
    obj_model = Hook
    
    def _query(self, bot, obj):
        return obj.kik_recipients.all()
    
    def _creator(self, obj, serializer):
        return KikRecipient.objects.create(chat_id=serializer.data['chat_id'],
                                           name=serializer.data['name'],
                                           username=serializer.data['username'],
                                           hook=obj)
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of kik recipients of a hook
        ---
        serializer: KikRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(KikRecipientList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new kik recipient to a handler
        ---
        serializer: KikRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(KikRecipientList, self).post(request, bot_id, id, format)
    
class KikRecipientDetail(PermabotsAPIView):
    model = KikRecipient
    serializer = KikRecipientSerializer
    
    def get_hook(self, id, bot, user):
        try:
            hook = Hook.objects.get(id=id, bot=bot)
            if hook.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return hook
        except Hook.DoesNotExist:
            raise Http404    
     
    def _user(self, obj):
        return obj.hook.bot.owner
     
    def get_recipient(self, id, hook, user):
        try:
            obj = self.model.objects.get(id=id, hook=hook)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_id, hook_id, id, format=None):
        """
        Get recipient by id
        ---
        serializer: KikRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient)
        return Response(serializer.data)
    
    def put(self, request, bot_id, hook_id, id, format=None):
        """
        Update existing telegram recipient
        ---
        serializer: KikRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_id, hook_id, id, format=None):
        """
        Delete an existing kik recipient
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        recipient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   
    
class MessengerRecipientList(ObjectBotListView):
    serializer = MessengerRecipientSerializer
    obj_model = Hook
    
    def _query(self, bot, obj):
        return obj.messenger_recipients.all()
    
    def _creator(self, obj, serializer):
        return MessengerRecipient.objects.create(chat_id=serializer.data['chat_id'],
                                                 name=serializer.data['name'],
                                                 hook=obj)
        
    def get(self, request, bot_id, id, format=None):
        """
        Get list of Messenger recipients of a hook
        ---
        serializer: MessengerRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(MessengerRecipientList, self).get(request, bot_id, id, format)
    
    def post(self, request, bot_id, id, format=None):
        """
        Add a new messenger recipient to a handler
        ---
        serializer: MessengerRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(MessengerRecipientList, self).post(request, bot_id, id, format)
    
class MessengerRecipientDetail(PermabotsAPIView):
    model = MessengerRecipient
    serializer = MessengerRecipientSerializer
    
    def get_hook(self, id, bot, user):
        try:
            hook = Hook.objects.get(id=id, bot=bot)
            if hook.bot.owner != user:
                raise exceptions.AuthenticationFailed()
            return hook
        except Hook.DoesNotExist:
            raise Http404    
     
    def _user(self, obj):
        return obj.hook.bot.owner
     
    def get_recipient(self, id, hook, user):
        try:
            obj = self.model.objects.get(id=id, hook=hook)
            if self._user(obj) != user:
                raise exceptions.AuthenticationFailed()
            return obj
        except self.model.DoesNotExist:
            raise Http404
         
    def get(self, request, bot_id, hook_id, id, format=None):
        """
        Get recipient by id
        ---
        serializer: MessengerRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient)
        return Response(serializer.data)
    
    def put(self, request, bot_id, hook_id, id, format=None):
        """
        Update existing telegram recipient
        ---
        serializer: MessengerRecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        serializer = self.serializer(recipient, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_id, hook_id, id, format=None):
        """
        Delete an existing Messenger recipient
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_id, request.user)
        hook = self.get_hook(hook_id, bot, request.user)
        recipient = self.get_recipient(id, hook, request.user)
        recipient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   