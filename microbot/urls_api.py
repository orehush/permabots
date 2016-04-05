from django.conf.urls import url
from microbot import views


def uuidzy(url):
    return url.replace('%u', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

# bots api
urlpatterns = [
    url(r'^bots/$', views.BotList.as_view(), name='bot-list'),
    url(uuidzy(r'^bots/(?P<id>%u)/$'), views.BotDetail.as_view(), name='bot-detail')]

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
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<id>%u)/recipients/$'), views.RecipientList.as_view(), name='hook-recipient-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/hooks/(?P<hook_id>%u)/recipients/(?P<id>%u)/$'), views.RecipientDetail.as_view(), 
        name='hook-recipient-list')]

# states api
urlpatterns += [
    url(uuidzy(r'^bots/(?P<bot_id>%u)/states/$'), views.StateList.as_view(), name='state-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/states/(?P<id>%u)/$'), views.StateDetail.as_view(), name='state-detail'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/$'), views.ChatStateList.as_view(), name='chatstate-list'),
    url(uuidzy(r'^bots/(?P<bot_id>%u)/chatstates/(?P<id>%u)/$'), views.ChatStateDetail.as_view(), name='chatstate-detail')]
