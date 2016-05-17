from rest_framework import serializers
from permabots.models import State, TelegramChatState, TelegramChat, TelegramUser, KikChatState, KikChat, KikUser, MessengerChatState
from django.utils.translation import ugettext_lazy as _


class StateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("State ID"))
    
    class Meta:
        model = State
        fields = ['id', 'created_at', 'updated_at', 'name']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
class TelegramChatStateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Chat State ID"))
    chat = serializers.IntegerField(source="chat.id", help_text=_("Chat identifier. Telegram API format. https://core.telegram.org/bots/api#chat"))
    state = StateSerializer(many=False, help_text=_("State associated to the Chat"))
    user = serializers.IntegerField(source="user.id", help_text=_("User indentifier. Telegram API format. https://core.telegram.org/bots/api#chat"))
    
    class Meta:
        model = TelegramChatState
        fields = ['id', 'created_at', 'updated_at', 'chat', 'user', 'state']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
    def create(self, validated_data):
        chat = TelegramChat.objects.get(pk=validated_data['chat'])
        user = TelegramUser.objects.get(pk=validated_data['user'])
        state = State.objects.get(name=validated_data['state']['name'])

        chat_state = TelegramChatState.objects.create(chat=chat,
                                                      state=state,
                                                      user=user)            
            
        return chat_state
    
    def update(self, instance, validated_data):
        chat = TelegramChat.objects.get(pk=validated_data['chat']['id'])   
        user = TelegramUser.objects.get(pk=validated_data['user']['id'])     
        state = State.objects.get(name=validated_data['state']['name'])
       
        instance.chat = chat
        instance.user = user
        instance.state = state   
        instance.save()
        return instance
    
class TelegramChatStateUpdateSerializer(TelegramChatStateSerializer):
    chat = serializers.IntegerField(source="chat.id", required=False, 
                                    help_text=_("Chat identifier. Telegram API format. https://core.telegram.org/bots/api#chat"))
    state = StateSerializer(many=False, required=False, help_text=_("State associated to the Chat"))
    user = serializers.IntegerField(source="user.id", required=False,
                                    help_text=_("User identifier. Telegram API format. https://core.telegram.org/bots/api#chat"))

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            instance.user = TelegramUser.objects.get(pk=validated_data['user']['id'])    
        if 'chat' in validated_data:
            instance.chat = TelegramChat.objects.get(pk=validated_data['chat']['id'])       
        if 'state' in validated_data:
            instance.state = State.objects.get(name=validated_data['state']['name'])
       
        instance.save()
        return instance
    

class KikChatStateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Chat State ID"))
    chat = serializers.CharField(source="chat.id", help_text=_("Chat identifier. Kik API format."))
    state = StateSerializer(many=False, help_text=_("State associated to the Chat"))
    user = serializers.CharField(source="user.username", help_text=_("User indentifier. Kik API format"))
    
    class Meta:
        model = KikChatState
        fields = ['id', 'created_at', 'updated_at', 'chat', 'user', 'state']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
    def create(self, validated_data):
        chat = KikChat.objects.get(pk=validated_data['chat'])
        user = KikUser.objects.get(pk=validated_data['user'])
        state = State.objects.get(name=validated_data['state']['name'])

        chat_state = KikChatState.objects.create(chat=chat,
                                                 state=state,
                                                 user=user)            
            
        return chat_state
    
    def update(self, instance, validated_data):
        chat = KikChat.objects.get(pk=validated_data['chat']['id'])   
        user = KikUser.objects.get(pk=validated_data['user']['username'])     
        state = State.objects.get(name=validated_data['state']['name'])
       
        instance.chat = chat
        instance.user = user
        instance.state = state   
        instance.save()
        return instance
    
class KikChatStateUpdateSerializer(KikChatStateSerializer):
    chat = serializers.CharField(source="chat.id", required=False, 
                                 help_text=_("Chat identifier. Kik API format."))
    state = StateSerializer(many=False, required=False, help_text=_("State associated to the Chat"))
    user = serializers.CharField(source="user.username", required=False,
                                 help_text=_("User identifier. Kik API format."))

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            instance.user = KikUser.objects.get(pk=validated_data['user']['username'])    
        if 'chat' in validated_data:
            instance.chat = KikChat.objects.get(pk=validated_data['chat']['id'])       
        if 'state' in validated_data:
            instance.state = State.objects.get(name=validated_data['state']['name'])
       
        instance.save()
        return instance
    
    
class MessengerChatStateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Chat State ID"))
    chat = serializers.CharField(help_text=_("Chat identifier. Messenger API format."))
    state = StateSerializer(many=False, help_text=_("State associated to the Chat"))
   
    class Meta:
        model = MessengerChatState
        fields = ['id', 'created_at', 'updated_at', 'chat', 'state']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
    def create(self, validated_data):
        chat = validated_data['chat']
        state = State.objects.get(name=validated_data['state']['name'])

        chat_state = MessengerChatState.objects.create(chat=chat,
                                                       state=state)            
            
        return chat_state
    
    def update(self, instance, validated_data):
        chat = validated_data['chat']
        state = State.objects.get(name=validated_data['state']['name'])
       
        instance.chat = chat
        instance.state = state   
        instance.save()
        return instance
    
class MessengerChatStateUpdateSerializer(MessengerChatStateSerializer):
    chat = serializers.CharField(required=False, 
                                 help_text=_("Chat identifier. Messenger API format."))
    state = StateSerializer(many=False, required=False, help_text=_("State associated to the Chat"))

    def update(self, instance, validated_data):
        if 'chat' in validated_data:
            instance.chat = validated_data['chat']       
        if 'state' in validated_data:
            instance.state = State.objects.get(name=validated_data['state']['name'])
       
        instance.save()
        return instance