from rest_framework import serializers
from microbot.models import Bot
from microbot.serializers import UserAPISerializer
from django.utils.translation import ugettext_lazy as _

class BotSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Bot ID"))
    info = UserAPISerializer(many=False, source='user_api', read_only=True,
                             help_text=_("Telegram API info. Automatically retrieved from Telegram"))
    
    class Meta:
        model = Bot
        fields = ('id', 'token', 'created_at', 'updated_at', 'enabled', 'info')
        read_only_fields = ('id', 'created_at', 'updated_at', 'info')
        
class BotUpdateSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(required=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = Bot
        fields = ('enabled', )