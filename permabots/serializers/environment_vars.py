from rest_framework import serializers
from permabots.models import EnvironmentVar
from django.utils.translation import ugettext_lazy as _


class EnvironmentVarSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(help_text=_("Environment variable ID"))
    
    class Meta:
        model = EnvironmentVar
        fields = ('id', 'created_at', 'updated_at', 'key', 'value')
        read_only_fields = ('id', 'created_at', 'updated_at',)