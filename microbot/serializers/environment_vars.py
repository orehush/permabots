from rest_framework import serializers
from microbot.models import EnvironmentVar

class EnvironmentVarSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = EnvironmentVar
        fields = ('id', 'created_at', 'updated_at', 'key', 'value')
        read_only_fields = ('id', 'created_at', 'updated_at',)