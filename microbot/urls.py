from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from microbot import views


uuid_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

urlpatterns = [
    url(r'^telegrambot/(?P<token>[-_:a-zA-Z0-9]+)/$', csrf_exempt(views.WebhookView.as_view()), name='telegrambot'),
    url(r'^hook/(?P<key>\w+)/$', csrf_exempt(views.HookView.as_view()), name='hook'),
    url(r'^api/bots/$', views.BotList.as_view(), name='bot-list'),
    url(r'^api/bots/(?P<pk>%s)/$' % uuid_regex, views.BotDetail.as_view(), name='bot-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/env/$' % uuid_regex, views.EnvironmentVarList.as_view(), name='env-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/env/(?P<pk>%s)/$' % (uuid_regex, uuid_regex), views.EnvironmentVarDetail.as_view(), name='env-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/$' % uuid_regex, views.HandlerList.as_view(), name='handler-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<pk>%s)/$' % (uuid_regex, uuid_regex), views.HandlerDetail.as_view(), name='handler-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<pk>%s)/urlparams/$' % (uuid_regex, uuid_regex), views.UrlParameterList.as_view(), 
        name='handler-urlparameter-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<handler_pk>%s)/urlparams/(?P<pk>%s)/$' % (uuid_regex, uuid_regex, uuid_regex), 
        views.UrlParameterDetail.as_view(), name='handler-urlparameter-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<pk>%s)/headerparams/$' % (uuid_regex, uuid_regex), views.HeaderParameterList.as_view(), 
        name='handler-headerparameter-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<handler_pk>%s)/headerparams/(?P<pk>%s)/$' % (uuid_regex, uuid_regex, uuid_regex), 
        views.HeaderParameterDetail.as_view(), name='handler-headerparameter-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<pk>%s)/sourcestates/$' % (uuid_regex, uuid_regex), views.SourceStateList.as_view(), 
        name='handler-sourcestate-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/handlers/(?P<handler_pk>%s)/sourcestates/(?P<pk>%s)/$' % (uuid_regex, uuid_regex, uuid_regex), 
        views.SourceStateDetail.as_view(), name='handler-sourcestate-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/hooks/$' % uuid_regex, views.HookList.as_view(), name='hook-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/hooks/(?P<pk>%s)/$' % (uuid_regex, uuid_regex), views.HookDetail.as_view(), name='hook-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/hooks/(?P<pk>%s)/recipients/$' % (uuid_regex, uuid_regex), views.RecipientList.as_view(), name='hook-recipient-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/hooks/(?P<hook_pk>%s)/recipients/(?P<pk>%s)/$' % (uuid_regex, uuid_regex, uuid_regex), views.RecipientDetail.as_view(), 
        name='hook-recipient-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/states/$' % uuid_regex, views.StateList.as_view(), name='state-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/states/(?P<pk>%s)/$' % (uuid_regex, uuid_regex), views.StateDetail.as_view(), name='state-detail'),
    url(r'^api/bots/(?P<bot_pk>%s)/chatstates/$' % uuid_regex, views.ChatStateList.as_view(), name='chatstate-list'),
    url(r'^api/bots/(?P<bot_pk>%s)/chatstates/(?P<pk>%s)/$' % (uuid_regex, uuid_regex), views.ChatStateDetail.as_view(), name='chatstate-detail'),
    
]
