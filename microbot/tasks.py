from __future__ import absolute_import
from celery import shared_task
from microbot.models import Update, Bot
import logging
import traceback
import sys


logger = logging.getLogger(__name__)

@shared_task
def handle_update(update_id, bot_id):
    try:
        update = Update.objects.get(update_id=update_id)
        bot = Bot.objects.get(id=bot_id, enabled=True)
    except Update.DoesNotExist:
        logger.error("Update %s does not exists" % update_id)
    except Bot.DoesNotExist:
        logger.error("Bot  %s does not exists or disabled" % bot_id)
    else:
        try:
            bot.handle(update)
        except:           
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            logger.error("Error processing %s for bot %s" % (update, bot))
