from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from microbot import views


def uuidzy(url):
    return url.replace('%u', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# hooks
urlpatterns = [
    url(r'^telegrambot/(?P<token>[-_:a-zA-Z0-9]+)/$', csrf_exempt(views.TelegramHookView.as_view()), name='telegrambot'),
    url(r'^hook/(?P<key>\w+)/$', csrf_exempt(views.MicrobotHookView.as_view()), name='hook')]

# bots api
urlpatterns += [
    url(r'^api/bots/$', views.BotList.as_view(), name='bot-list'),
    url(uuidzy(r'^api/bots/(?P<pk>%u)/$'), views.BotDetail.as_view(), name='bot-detail')]

# environment variables api
urlpatterns += [
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/env/$'), views.EnvironmentVarList.as_view(), name='env-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/env/(?P<pk>%u)/$'), views.EnvironmentVarDetail.as_view(), name='env-list')]
    
# handlers api
urlpatterns += [
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/$'), views.HandlerList.as_view(), name='handler-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<pk>%u)/$'), views.HandlerDetail.as_view(), name='handler-detail'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<pk>%u)/urlparams/$'), views.UrlParameterList.as_view(), 
        name='handler-urlparameter-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<handler_pk>%u)/urlparams/(?P<pk>%u)/$'), 
        views.UrlParameterDetail.as_view(), name='handler-urlparameter-detail'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<pk>%u)/headerparams/$'), views.HeaderParameterList.as_view(), 
        name='handler-headerparameter-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<handler_pk>%u)/headerparams/(?P<pk>%u)/$'), 
        views.HeaderParameterDetail.as_view(), name='handler-headerparameter-detail'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<pk>%u)/sourcestates/$'), views.SourceStateList.as_view(), 
        name='handler-sourcestate-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/handlers/(?P<handler_pk>%u)/sourcestates/(?P<pk>%u)/$'), 
        views.SourceStateDetail.as_view(), name='handler-sourcestate-detail')]

# hooks api
urlpatterns += [
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/hooks/$'), views.HookList.as_view(), name='hook-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/hooks/(?P<pk>%u)/$'), views.HookDetail.as_view(), name='hook-detail'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/hooks/(?P<pk>%u)/recipients/$'), views.RecipientList.as_view(), name='hook-recipient-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/hooks/(?P<hook_pk>%u)/recipients/(?P<pk>%u)/$'), views.RecipientDetail.as_view(), 
        name='hook-recipient-list')]

# states api
urlpatterns += [
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/states/$'), views.StateList.as_view(), name='state-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/states/(?P<pk>%u)/$'), views.StateDetail.as_view(), name='state-detail'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/chatstates/$'), views.ChatStateList.as_view(), name='chatstate-list'),
    url(uuidzy(r'^api/bots/(?P<bot_pk>%u)/chatstates/(?P<pk>%u)/$'), views.ChatStateDetail.as_view(), name='chatstate-detail')]
