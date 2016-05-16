from rest_framework import serializers
from permabots.models import Hook, TelegramRecipient, KikRecipient, Response, MessengerRecipient
from permabots.serializers import ResponseSerializer, ResponseUpdateSerializer
from django.utils.translation import ugettext_lazy as _


class TelegramRecipientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Recipient ID"))
    
    class Meta:
        model = TelegramRecipient
        fields = ('id', 'created_at', 'updated_at', 'name', 'chat_id')
        read_only_fields = ('id', 'created_at', 'updated_at', )


class KikRecipientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Recipient ID"))
    
    class Meta:
        model = KikRecipient
        fields = ('id', 'created_at', 'updated_at', 'name', 'chat_id', 'username')
        read_only_fields = ('id', 'created_at', 'updated_at', )
        
class MessengerRecipientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Recipient ID"))
    
    class Meta:
        model = MessengerRecipient
        fields = ('id', 'created_at', 'updated_at', 'name', 'chat_id')
        read_only_fields = ('id', 'created_at', 'updated_at', )

class HookSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Hook ID"))
    response = ResponseSerializer(many=False, help_text=_("Template the hook uses to generate the response"))
    telegram_recipients = TelegramRecipientSerializer(many=True, required=False, read_only=True, 
                                                      help_text=_("List of telegram recipients the hook responses to"))
    kik_recipients = KikRecipientSerializer(many=True, required=False, read_only=True, help_text=_("List of kik recipients the hook responses to"))
    
    class Meta:
        model = Hook
        fields = ('id', 'created_at', 'updated_at', 'name', 'key', 'enabled', 'response', 'telegram_recipients', 'kik_recipients')
        read_only_fields = ('id', 'created_at', 'updated_at', 'key', 'telegram_recipients', 'kik_recipients')
    
    def _create_recipients(self, recipients, hook):
        for recipient in recipients:
            TelegramRecipient.objects.get_or_create(chat_id=recipient['chat_id'],
                                                    name=recipient['name'],
                                                    hook=hook)
            
    def _update_recipients(self, recipients, instance):
        instance.telegram_recipients.all().delete()
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
    name = serializers.CharField(required=False, max_length=200, help_text=_("Name of the hook"))
    response = ResponseUpdateSerializer(many=False, required=False, help_text=_("Template the hook uses to generate the response"))   

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