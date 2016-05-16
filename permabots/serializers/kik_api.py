from rest_framework import serializers
from permabots.models import KikUser
from datetime import datetime
import time

class TimestampField(serializers.Field):

    def to_internal_value(self, data):
        return datetime.fromtimestamp(data/1000.)
    
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))
        
class KikMessageSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    chatId = serializers.CharField()
    # reserved word field 'from' changed dynamically
    from_ = serializers.CharField()
    timestamp = TimestampField()
    participants = serializers.ListField(required=False, child=serializers.CharField())
    body = serializers.CharField(required=False)
    type = serializers.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(KikMessageSerializer, self).__init__(*args, **kwargs)
        self.fields['from'] = self.fields['from_']
        del self.fields['from_']
        
    
class UserAPISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = KikUser
        fields = ('first_name', 'last_name', 'username')