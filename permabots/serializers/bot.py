from rest_framework import serializers
from permabots.models import Bot, TelegramBot, KikBot, MessengerBot
from permabots.serializers import UserAPISerializer
from django.utils.translation import ugettext_lazy as _

class MessengerBotSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Bot ID"))
    enabled = serializers.BooleanField(required=False, default=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = MessengerBot
        fields = ('id', 'created_at', 'updated_at', 'enabled', 'token')
        read_only_fields = ('id', 'created_at', 'updated_at')
        
class MessengerBotUpdateSerializer(serializers.HyperlinkedModelSerializer):
    enabled = serializers.BooleanField(required=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = MessengerBot
        fields = ('enabled', )

class KikBotSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Bot ID"))
    enabled = serializers.BooleanField(required=False, default=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = KikBot
        fields = ('id', 'api_key', 'created_at', 'updated_at', 'enabled', 'username')
        read_only_fields = ('id', 'created_at', 'updated_at')
        
class KikBotUpdateSerializer(serializers.HyperlinkedModelSerializer):
    enabled = serializers.BooleanField(required=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = KikBot
        fields = ('enabled', )


class TelegramBotSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Bot ID"))
    info = UserAPISerializer(many=False, source='user_api', read_only=True,
                             help_text=_("Telegram API info. Automatically retrieved from Telegram"))
    enabled = serializers.BooleanField(required=False, default=True, help_text=_("Enable/disable bot"))

    class Meta:
        model = TelegramBot
        fields = ('id', 'token', 'created_at', 'updated_at', 'enabled', 'info')
        read_only_fields = ('id', 'created_at', 'updated_at', 'info')
        
class TelegramBotUpdateSerializer(serializers.HyperlinkedModelSerializer):
    enabled = serializers.BooleanField(required=True, help_text=_("Enable/disable bot"))
    
    class Meta:
        model = TelegramBot
        fields = ('enabled', )

class BotSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Bot ID"))
    telegram_bot = TelegramBotSerializer(many=False, read_only=True)
    kik_bot = KikBotSerializer(many=False, read_only=True)
    messenger_bot = MessengerBotSerializer(many=False, read_only=True)
    
    class Meta:
        model = Bot
        fields = ('id', 'name', 'created_at', 'updated_at', 'telegram_bot', 'kik_bot', 'messenger_bot')
        read_only_fields = ('id', 'created_at', 'updated_at', 'telegram_bot', 'kik_bot', 'messenger_bot')
        
class BotUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Bot
        fields = ('name', )