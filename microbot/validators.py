import re
from django.core.exceptions import ValidationError
from jinja2 import Template
from django.utils.translation import ugettext_lazy as _
import ast
from jinja2.exceptions import TemplateSyntaxError
import sys
import logging
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser  # noqa

logger = logging.getLogger(__name__)

def validate_token(value):
    if not re.match('[0-9]+:[-_a-zA-Z0-9]+', value):
        raise ValidationError(_("%(value)s is not a valid token"), params={'value': value})
    
def validate_template(value):
    try:
        Template(value)
    except TemplateSyntaxError:
        exctype, value = sys.exc_info()[:2]
        raise ValidationError(_("Jinja error: %(error)s"), params={'error': value})
    except:
        exctype, value = sys.exc_info()[:2]
        logger.error("Unexpected jinja validation: (%s, %s)" % (exctype, value))
        raise ValidationError(_("Jinja template not valid"))
    
def validate_pattern(value):
    try:
        re.compile(value)
    except re.error:
        exctype, value = sys.exc_info()[:2]
        raise ValidationError(_("Not valid regular expression: %(error)s"), params={'error': value})
    except:
        exctype, value = sys.exc_info()[:2]
        logger.error("Unexpected pattern validation: (%s, %s)" % (exctype, value))
        raise ValidationError(_("Not valid regular expression"))
    
def validate_telegram_keyboard(value):
    try:
        # TODO: just check array after rendering template. Some cases are not validated
        # If template not valid let the other validator work
        try:
            template = Template(value)
        except:
            pass
        else:
            empty_context = {'env': {},
                             'response': {},
                             'pattern': {},
                             'state_context': {},
                             'message': {},
                             'emoji': {}}
            state_contexts = re.findall('state_context.(?P<element>\w+)', value)
            for state_context in state_contexts:
                empty_context['state_context'][state_context] = {'response': {}, 'pattern': {}}
            keyboard_text = template.render(**empty_context)
            if keyboard_text:
                ast.literal_eval(keyboard_text)
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
