from django.conf.urls import url
from permabots import views


def uuidzy(url):
    return url.replace('%u', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# bots api
urlpatterns = [
    url(r'^bots/$', views.BotList.as_view(), name='bot-list'),
    url(uuidzy(r'^bots/(?P<id>%u)/$'), views.BotDetail.as_view(), name='bot-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/telegram/$'), views.TelegramBotList.as_view(), name='bot-telegram-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/telegram/(?P<id>%u)/$'), views.TelegramBotDetail.as_view(), name='bot-telegram-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/kik/$'), views.KikBotList.as_view(), name='bot-kik-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/kik/(?P<id>%u)/$'), views.KikBotDetail.as_view(), name='bot-kik-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/messenger/$'), views.MessengerBotList.as_view(), name='bot-messenger-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/messenger/(?P<id>%u)/$'), views.MessengerBotDetail.as_view(), name='bot-messenger-detail')]

# environment variables api
urlpatterns += [
    url(uuidzy(r'^bots/(?P<bot_id>%u)/env/$'), views.EnvironmentVarList.as_view(), name='env-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/env/(?P<id>%u)/$'), views.EnvironmentVarDetail.as_view(), name='env-list')]
    
# handlers api
urlpatterns += [
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/$'), views.HandlerList.as_view(), name='handler-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<id>%u)/$'), views.HandlerDetail.as_view(), name='handler-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<id>%u)/urlparams/$'), views.UrlParameterList.as_view(), 
        name='handler-urlparameter-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<handler_id>%u)/urlparams/(?P<id>%u)/$'), 
        views.UrlParameterDetail.as_view(), name='handler-urlparameter-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<id>%u)/headerparams/$'), views.HeaderParameterList.as_view(), 
        name='handler-headerparameter-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<handler_id>%u)/headerparams/(?P<id>%u)/$'), 
        views.HeaderParameterDetail.as_view(), name='handler-headerparameter-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<id>%u)/sourcestates/$'), views.SourceStateList.as_view(), 
        name='handler-sourcestate-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/handlers/(?P<handler_id>%u)/sourcestates/(?P<id>%u)/$'), 
        views.SourceStateDetail.as_view(), name='handler-sourcestate-detail')]

# hooks api
urlpatterns += [
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/$'), views.HookList.as_view(), name='hook-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<id>%u)/$'), views.HookDetail.as_view(), name='hook-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<id>%u)/recipients/telegram/$'), views.TelegramRecipientList.as_view(), name='hook-recipient-telegram-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<hook_id>%u)/recipients/telegram/(?P<id>%u)/$'), views.TelegramRecipientDetail.as_view(), 
        name='hook-recipient-telegram-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<id>%u)/recipients/kik/$'), views.KikRecipientList.as_view(), name='hook-recipient-kik-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<hook_id>%u)/recipients/kik/(?P<id>%u)/$'), views.KikRecipientDetail.as_view(), 
        name='hook-recipient-kik-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<id>%u)/recipients/messenger/$'), views.MessengerRecipientList.as_view(), name='hook-recipient-messenger-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<hook_id>%u)/recipients/messenger/(?P<id>%u)/$'), views.MessengerRecipientDetail.as_view(), 
        name='hook-recipient-messenger-detail')]

# states api
urlpatterns += [
    url(uuidzy(r'^bots/(?P<bot_id>%u)/states/$'), views.StateList.as_view(), name='state-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/states/(?P<id>%u)/$'), views.StateDetail.as_view(), name='state-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/telegram/$'), views.TelegramChatStateList.as_view(), name='telegram-chatstate-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/telegram/(?P<id>%u)/$'), views.TelegramChatStateDetail.as_view(), name='telegram-chatstate-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/kik/$'), views.KikChatStateList.as_view(), name='kik-chatstate-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/kik/(?P<id>%u)/$'), views.KikChatStateDetail.as_view(), name='kik-chatstate-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/messenger/$'), views.MessengerChatStateList.as_view(), name='messenger-chatstate-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/messenger/(?P<id>%u)/$'), views.MessengerChatStateDetail.as_view(), name='messenger-chatstate-detail')]
