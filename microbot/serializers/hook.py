from rest_framework import serializers
from microbot.models import Hook, Recipient, Response
from microbot.serializers import ResponseSerializer, ResponseUpdateSerializer

class RecipientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = Recipient
        fields = ('id', 'created_at', 'updated_at', 'name', 'chat_id')
        read_only_fields = ('id', 'created_at', 'updated_at', )

class HookSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    response = ResponseSerializer(many=False)
    recipients = RecipientSerializer(many=True, required=False, read_only=True)
    
    class Meta:
        model = Hook
        fields = ('id', 'created_at', 'updated_at', 'name', 'key', 'enabled', 'response', 'recipients')
        read_only_fields = ('id', 'created_at', 'updated_at', 'key', 'recipients')
    
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

class HookUpdateSerializer(HookSerializer):
    name = serializers.CharField(required=False, max_length=200)
    response = ResponseUpdateSerializer(many=False, required=False)   

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.enabled = validated_data.get('enabled', instance.enabled)
        if 'response' in validated_data:
            instance.response.text_template = validated_data['response'].get('text_template', instance.response.text_template)
            instance.response.keyboard_template = validated_data['response'].get('keyboard_template', instance.response.keyboard_template)
            instance.response.save()
            
        if 'recipients' in validated_data:
            self._update_recipients(validated_data['recipients'], instance)
    
        instance.save()
        return instance    