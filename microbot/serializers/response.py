from rest_framework import serializers
from microbot.models import Response

class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ('text_template', 'keyboard_template')
        
class ResponseUpdateSerializer(ResponseSerializer):
    text_template = serializers.CharField(required=False, max_length=1000)
    keyboard_template = serializers.CharField(required=False, max_length=1000)