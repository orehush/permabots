from rest_framework import serializers
from microbot.models import Bot
from microbot.serializers import UserAPISerializer


class BotSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    info = UserAPISerializer(many=False, source='user_api', read_only=True)
    
    class Meta:
        model = Bot
        fields = ('id', 'token', 'created_at', 'updated_at', 'enabled', 'info')
        read_only_fields = ('id', 'created_at', 'updated_at', 'info')
        
class BotUpdateSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(required=True)
    
    class Meta:
        model = Bot
        fields = ('enabled', )