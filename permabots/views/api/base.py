from rest_framework.views import APIView
from permabots.models import Bot
from rest_framework.response import Response
from rest_framework import status
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http.response import Http404
from rest_framework import exceptions


logger = logging.getLogger(__name__)


class PermabotsAPIView(APIView):
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
        
        
class ListBotAPIView(PermabotsAPIView):
    serializer = None
    many = True

    def _query(self, bot):
        raise NotImplemented
    
    def _creator(self, bot, serializer):
        raise NotImplemented
    
    def get(self, request, bot_pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        serializer = self.serializer(self._query(bot), many=self.many)
        return Response(serializer.data)
    
    def post(self, request, bot_pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            obj = self._creator(bot, serializer)
            return Response(self.serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
class DetailBotAPIView(PermabotsAPIView):
    model = None
    serializer = None
    serializer_update = None
    
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
        if self.serializer_update:
            serializer = self.serializer_update(obj, data=request.data)
        else:
            serializer = self.serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(self.serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bot_pk, pk, format=None):
        bot = self.get_bot(bot_pk, request.user)
        obj = self.get_object(pk, bot, request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ObjectBotListView(PermabotsAPIView):
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
            obj = self._creator(obj, serializer)
            return Response(self.serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 