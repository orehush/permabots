from rest_framework import serializers
from microbot.models import User, Chat, Message, Update, Bot, EnvironmentVar, Handler, Request, UrlParam, HeaderParam, \
    Response, Hook, Recipient, State, ChatState
from datetime import datetime
import time


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')
        
class ChatSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Chat
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
        model = Message
        fields = ('message_id', 'from_', 'date', 'chat', 'text')
        
class UpdateSerializer(serializers.HyperlinkedModelSerializer):
    update_id = serializers.IntegerField()
    message = MessageSerializer(many=False)
    
    class Meta:
        model = Update
        fields = ('update_id', 'message')
        
    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data['message']['from_user'])
        
        chat, _ = Chat.objects.get_or_create(**validated_data['message']['chat'])           
        
        message, _ = Message.objects.get_or_create(message_id=validated_data['message']['message_id'],
                                                   from_user=user,
                                                   date=validated_data['message']['date'],
                                                   chat=chat,
                                                   text=validated_data['message']['text'])
        update, _ = Update.objects.get_or_create(update_id=validated_data['update_id'],
                                                 message=message)

        return update
    
class UserAPISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')
        
class StateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = State
        fields = ['id', 'created_at', 'updated_at', 'name']
        read_only_fields = ('id', 'created_at', 'updated_at',)

class BotSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    info = UserAPISerializer(many=False, source='user_api', read_only=True)
    
    class Meta:
        model = Bot
        fields = ('id', 'token', 'created_at', 'updated_at', 'enabled', 'info')
        read_only_fields = ('id', 'created_at', 'updated_at', 'info')
        
class EnvironmentVarSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = EnvironmentVar
        fields = ('id', 'created_at', 'updated_at', 'key', 'value')
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
class AbsParamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = UrlParam
        fields = ('id', 'created_at', 'updated_at', 'key', 'value_template')      
        read_only_fields = ('id', 'created_at', 'updated_at',)  
        
class RequestSerializer(serializers.HyperlinkedModelSerializer):
    url_parameters = AbsParamSerializer(many=True, required=False)
    header_parameters = AbsParamSerializer(many=True, required=False)
    
    class Meta:
        model = Request
        fields = ('url_template', 'method', 'data', 'url_parameters', 'header_parameters')
        
class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ('text_template', 'keyboard_template')
        
class HandlerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    request = RequestSerializer(many=False, required=False)
    response = ResponseSerializer(many=False)
    target_state = StateSerializer(many=False, required=False)
    source_states = StateSerializer(many=True, required=False)
    priority = serializers.IntegerField(required=False)

    class Meta:
        model = Handler
        fields = ('id', 'created_at', 'updated_at', 'name', 'pattern', 'enabled', 'request', 'response', 'target_state', 'source_states', 'priority')
        read_only = ('source_states', 'id', 'created_at', 'updated_at',)
        
    def _create_params(self, params, model, request):
        for param in params:
            model.objects.get_or_create(key=param['key'],
                                        value_template=param['value_template'],
                                        request=request)  
                
    def _update_params(self, params, query_get):
        for param in params:
            instance_param = query_get(key=param['key'])
            instance_param.key = param['key']
            instance_param.value_template = param['value_template']
            instance_param.save()
                   
    def create(self, validated_data):
        state = None
        request = None
        if 'target_state' in validated_data:
            state, _ = Request.objects.get_or_create(**validated_data['target_state'])
        if 'request' in validated_data:
            request, _ = Request.objects.get_or_create(**validated_data['request'])
            self._create_params(validated_data['request']['url_parameters'], UrlParam, request)
            self._create_params(validated_data['request']['header_parameters'], HeaderParam, request)
            
        response, _ = Response.objects.get_or_create(**validated_data['response'])
        
        handler, _ = Handler.objects.get_or_create(pattern=validated_data['pattern'],
                                                   response=response,
                                                   enabled=validated_data['enabled'],
                                                   request=request,
                                                   target_state=state,
                                                   priority=validated_data.get('priority', 0))
        
        return handler
    
    def update(self, instance, validated_data):
        instance.pattern = validated_data.get('name', instance.name)
        instance.pattern = validated_data.get('pattern', instance.pattern)
        instance.enabled = validated_data.get('enabled', instance.enabled)
        instance.priority = validated_data.get('priority', instance.priority)
        if 'target_state' in validated_data:
            state, _ = State.objects.get_or_create(bot=instance.bot,
                                                   name=validated_data['target_state']['name'])
            instance.target_state = state
        
        instance.response.text_template = validated_data['response'].get('text_template', instance.response.text_template)
        instance.response.keyboard_template = validated_data['response'].get('keyboard_template', instance.response.keyboard_template)
        instance.response.save()

        if 'request' in validated_data:
            instance.request.url_template = validated_data['request'].get('url_template', instance.request.url_template)
            instance.request.method = validated_data['request'].get('method', instance.request.method)
            instance.request.data = validated_data['request'].get('data', instance.request.data)
            instance.request.save()
        
            self._update_params(validated_data['request']['url_parameters'], instance.request.url_parameters.get)
            self._update_params(validated_data['request']['header_parameters'], instance.request.header_parameters.get)
            
        instance.save()
        return instance
    
class RecipientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = Recipient
        fields = ('id', 'created_at', 'updated_at', 'name', 'chat_id')
        read_only_fields = ('id', 'created_at', 'updated_at',)

class HookSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    response = ResponseSerializer(many=False)
    recipients = RecipientSerializer(many=True, required=False)
    
    class Meta:
        model = Hook
        fields = ('id', 'created_at', 'updated_at', 'name', 'key', 'enabled', 'response', 'recipients')
        read_only_fields = ('id', 'created_at', 'updated_at', 'key', )
    
    def _create_recipients(self, recipients, hook):
        for recipient in recipients:
            Recipient.objects.get_or_create(chat_id=recipient['chat_id'],
                                            name=recipient['name'],
                                            hook=hook)
            
    def _update_recipients(self, recipients, instance):
        instance.recipients.all().delete()
        self._create_recipients(recipients, instance)            
        
    def create(self, validated_data):
        response, _ = Response.objects.get_or_create(**validated_data['response'])
        
        hook, _ = Hook.objects.get_or_create(response=response,
                                             enabled=validated_data['enabled'],
                                             name=validated_data['name'])
        
        self._create_recipients(validated_data['recipients'], hook)
            
        return hook
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.enabled = validated_data.get('enabled', instance.enabled)
        
        instance.response.text_template = validated_data['response'].get('text_template', instance.response.text_template)
        instance.response.keyboard_template = validated_data['response'].get('keyboard_template', instance.response.keyboard_template)
        instance.response.save()
        
        self._update_recipients(validated_data['recipients'], instance)
    
        instance.save()
        return instance
    
class ChatStateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    chat = serializers.IntegerField(source="chat.id")
    state = StateSerializer(many=False)
    
    class Meta:
        model = ChatState
        fields = ['id', 'created_at', 'updated_at', 'chat', 'state']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
    def create(self, validated_data):
        chat = Chat.objects.get(pk=validated_data['chat'])        
        state = State.objects.get(name=validated_data['state']['name'])

        chat_state = ChatState.objects.create(chat=chat,
                                              state=state)            
            
        return chat_state
    
    def update(self, instance, validated_data):
        chat = Chat.objects.get(pk=validated_data['chat']['id'])        
        state = State.objects.get(name=validated_data['state']['name'])
       
        instance.chat = chat
        instance.state = state   
        instance.save()
        return instance