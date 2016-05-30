from rest_framework import serializers
from permabots.models import TelegramUser, TelegramChat, TelegramMessage, TelegramUpdate, TelegramCallbackQuery
from datetime import datetime
import time


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = TelegramUser
        fields = ('id', 'first_name', 'last_name', 'username')
        
class ChatSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = TelegramChat
        fields = ('id', 'type', 'title', 'username', 'first_name', 'last_name')
        
class TimestampField(serializers.Field):

    def to_internal_value(self, data):
        return datetime.fromtimestamp(data)
    
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))

        
class MessageSerializer(serializers.HyperlinkedModelSerializer):
    message_id = serializers.IntegerField()
    # reserved word field 'from' changed dynamically
    from_ = UserSerializer(many=False, source="from_user")
    chat = ChatSerializer(many=False)
    date = TimestampField()
    
    def __init__(self, *args, **kwargs):
        super(MessageSerializer, self).__init__(*args, **kwargs)
        self.fields['from'] = self.fields['from_']
        del self.fields['from_']

    class Meta:
        model = TelegramMessage
        fields = ('message_id', 'from_', 'date', 'chat', 'text')
        validators = []
        
class CallbackQuerySerializer(serializers.HyperlinkedModelSerializer):
    from_ = UserSerializer(many=False, source="from_user")
    message = MessageSerializer(many=False, required=False)
    id = serializers.CharField(source="callback_id")
    
    def __init__(self, *args, **kwargs):
        super(CallbackQuerySerializer, self).__init__(*args, **kwargs)
        self.fields['from'] = self.fields['from_']
        del self.fields['from_']
    
    class Meta:
        model = TelegramCallbackQuery
        fields = ('id', 'message', 'from_', 'data')
        validators = []        

        
class UpdateSerializer(serializers.HyperlinkedModelSerializer):
    update_id = serializers.IntegerField()
    message = MessageSerializer(many=False, required=False)
    callback_query = CallbackQuerySerializer(many=False, required=False)
    
    class Meta:
        model = TelegramUpdate
        fields = ('update_id', 'message', 'callback_query')
        validators = []
    
class UserAPISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ('first_name', 'last_name', 'username')