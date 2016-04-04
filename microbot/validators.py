import re
from django.core.exceptions import ValidationError
from jinja2 import Template
from django.utils.translation import ugettext_lazy as _
import ast
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser  # noqa

def validate_token(value):
    if not re.match('[0-9]+:[-_a-zA-Z0-9]+', value):
        raise ValidationError(_("%(value)s is not a valid token"), params={'value': value})
    
def validate_template(value):
    try:
        Template(value)
    except:
        raise ValidationError(_("Not correct jinja2 template: %(value)s"), params={'value': value})
    
def validate_pattern(value):
    try:
        re.compile(value)
    except:
        raise ValidationError(_("Not correct Regex: %(value)s"), params={'value': value})
    
def validate_telegram_keyboard(value):
    try:
        ast.literal_eval(value)
    except:
        raise ValidationError(_("Not correct keyboard: %(value)s. Check https://core.telegram.org/bots/api#replykeyboardmarkup"), params={'value': value})

def validate_telegram_text_html(value):
    tags = ['b', 'i', 'a', 'code', 'pre']
    found = []
    msg = _("Not correct HTML for Telegram message. Check https://core.telegram.org/bots/api#html-style")

    class TelegramHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            tags.index(tag)
            found.append(tag)          
   
        def handle_endtag(self, tag):
            found.pop(found.index(tag))
    parser = TelegramHTMLParser()
    try:
        parser.feed(value)
        if found:
            raise ValidationError(msg)
    except:
        raise ValidationError(msg)