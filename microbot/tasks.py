from __future__ import absolute_import
from celery import shared_task
from microbot.models import Update, TelegramBot, Hook
import logging
import traceback
import sys
from microbot import caching

logger = logging.getLogger(__name__)

@shared_task
def handle_update(update_id, bot_id):
    try:
        update = caching.get_or_set(Update, update_id)
        telegram_bot = caching.get_or_set(TelegramBot, bot_id)
    except Update.DoesNotExist:
        logger.error("Update %s does not exists" % update_id)
    except TelegramBot.DoesNotExist:
        logger.error("Bot  %s does not exists or disabled" % bot_id)
    except:
        logger.error("Error handling update %s from bot %s" % (update_id, bot_id))
    else:
        try:
            telegram_bot.bot.handle_message(update.message, telegram_bot)
        except:           
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            logger.error("Error processing %s for bot %s" % (update, telegram_bot))
        else:
            # Each update is only used once
            caching.delete(Update, update)
            
@shared_task
def handle_hook(hook_id, data):
    try:
        hook = Hook.objects.get(id=hook_id)
    except Hook.DoesNotExist:
        logger.error("Hook %s does not exists" % hook_id)
    else:
        try:
            hook.bot.handle_hook(hook, data)
        except:           
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            logger.error("Error processing %s for bot %s" % (hook, hook.bot))
