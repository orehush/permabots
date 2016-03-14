from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from microbot import views

urlpatterns = [
    url(r'^telegrambot/(?P<token>[-_:a-zA-Z0-9]+)/$', csrf_exempt(views.WebhookView.as_view()), name='telegrambot'),
    url(r'^api/bots/$', views.BotList.as_view(), name='bot-list'),
    url(r'^api/bots/(?P<pk>[0-9]+)/$', views.BotDetail.as_view(), name='bot-detail'),
    url(r'^api/bots/(?P<bot_pk>[0-9]+)/env/$', views.EnvironmentVarList.as_view(), name='env-list'),
    url(r'^api/bots/(?P<bot_pk>[0-9]+)/env/(?P<pk>[0-9]+)/$', views.EnvironmentVarDetail.as_view(), name='env-list'),
    url(r'^api/bots/(?P<bot_pk>[0-9]+)/handlers/$', views.HandlerList.as_view(), name='handler-list'),
    url(r'^api/bots/(?P<bot_pk>[0-9]+)/handlers/(?P<pk>[0-9]+)/$', views.HandlerDetail.as_view(), name='handler-detail'),
]
