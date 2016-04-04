from rest_framework import serializers
from microbot.models import Response
from microbot import validators


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ('text_template', 'keyboard_template')
        
class ResponseUpdateSerializer(ResponseSerializer):
    text_template = serializers.CharField(required=False, max_length=1000,
                                          validators=[validators.validate_template, validators.validate_telegram_text_html])
    keyboard_template = serializers.CharField(required=False, max_length=1000, 
                                              validators=[validators.validate_template, validators.validate_telegram_keyboard])