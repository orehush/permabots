from rest_framework import serializers
from permabots.models import Response
from permabots import validators
from django.utils.translation import ugettext_lazy as _

class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ('text_template', 'keyboard_template')
        
class ResponseUpdateSerializer(ResponseSerializer):
    text_template = serializers.CharField(required=False, max_length=1000,
                                          validators=[validators.validate_template, validators.validate_telegram_text_html],
                                          help_text=_("Template to generate text response. In jinja2 format. http://jinja.pocoo.org/"))
    keyboard_template = serializers.CharField(required=False, max_length=1000, 
                                              validators=[validators.validate_template, validators.validate_telegram_keyboard],
                                              help_text=_("Template to generate keyboard response. In jinja2 format. http://jinja.pocoo.org/"))