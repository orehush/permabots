from rest_framework import serializers
from microbot.models import State, ChatState, Chat

class StateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = State
        fields = ['id', 'created_at', 'updated_at', 'name']
        read_only_fields = ('id', 'created_at', 'updated_at',)
        
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
    
class ChatStateUpdateSerializer(ChatStateSerializer):
    chat = serializers.IntegerField(source="chat.id", required=False)
    state = StateSerializer(many=False, required=False)
    
    def update(self, instance, validated_data):
        if 'chat' in validated_data:
            instance.chat = Chat.objects.get(pk=validated_data['chat']['id'])       
        if 'state' in validated_data:
            instance.state = State.objects.get(name=validated_data['state']['name'])
       
        instance.save()
        return instance