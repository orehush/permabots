from microbot.serializers import HookSerializer, RecipientSerializer, HookUpdateSerializer
from microbot.models import Hook, Recipient
from microbot.models import Response as handlerResponse
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http.response import Http404
from rest_framework import exceptions
from microbot.views.api.base import MicrobotAPIView, ListBotAPIView, DetailBotAPIView, ObjectBotListView


logger = logging.getLogger(__name__)


class HookList(ListBotAPIView):
    serializer = HookSerializer
    
    def _query(self, bot):
        return bot.hooks.all()
    
    def _creator(self, bot, serializer):
        
        response = handlerResponse.objects.create(text_template=serializer.data['response']['text_template'],
                                                  keyboard_template=serializer.data['response']['keyboard_template'])
        Hook.objects.create(bot=bot,
                            enabled=serializer.data['enabled'],
                            response=response,
                            name=serializer.data['name'])
        
    def get(self, request, bot_pk, format=None):
        """
        Get list of hooks
        ---
        serializer: HookSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HookList, self).get(request, bot_pk, format)
    
    def post(self, request, bot_pk, format=None):
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
        return super(HookList, self).post(request, bot_pk, format)
    
    
class HookDetail(DetailBotAPIView):
    model = Hook
    serializer = HookSerializer
    serializer_update = HookUpdateSerializer
    
    def get(self, request, bot_pk, pk, format=None):
        """
        Get hook by id
        ---
        serializer: HookSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """        
        return super(HookDetail, self).get(request, bot_pk, pk, format)
    
    def put(self, request, bot_pk, pk, format=None):
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
        return super(HookDetail, self).put(request, bot_pk, pk, format)
        
    def delete(self, request, bot_pk, pk, format=None):
        """
        Delete existing hook
        ---
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(HookDetail, self).delete(request, bot_pk, pk, format)
    
class RecipientList(ObjectBotListView):
    serializer = RecipientSerializer
    obj_model = Hook
    
    def _query(self, bot, obj):
        return obj.recipients.all()
    
    def _creator(self, obj, serializer):
        Recipient.objects.create(chat_id=serializer.data['chat_id'],
                                 name=serializer.data['name'],
                                 hook=obj)
        
    def get(self, request, bot_pk, pk, format=None):
        """
        Get list of recipients of a hook
        ---
        serializer: RecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(RecipientList, self).get(request, bot_pk, pk, format)
    
    def post(self, request, bot_pk, pk, format=None):
        """
        Add a new recipient to a handler
        ---
        serializer: RecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        return super(RecipientList, self).post(request, bot_pk, pk, format)
    
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
        """
        Get recipient by id
        ---
        serializer: RecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        serializer = self.serializer(recipient)
        return Response(serializer.data)
    
    def put(self, request, bot_pk, hook_pk, pk, format=None):
        """
        Update existing recipient
        ---
        serializer: RecipientSerializer
        responseMessages:
            - code: 401
              message: Not authenticated
            - code: 400
              message: Not valid request
        """
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        serializer = self.serializer(recipient, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, bot_pk, hook_pk, pk, format=None):
        """
        Delete an existing recipient
        ---   
        responseMessages:
            - code: 401
              message: Not authenticated
        """
        bot = self.get_bot(bot_pk, request.user)
        hook = self.get_hook(hook_pk, bot, request.user)
        recipient = self.get_recipient(pk, hook, request.user)
        recipient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   