from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from microbot import views

urlpatterns = [
    url(r'^telegrambot/(?P<token>[-_:a-zA-Z0-9]+)/$', csrf_exempt(views.TelegramHookView.as_view()), name='telegrambot'),
    url(r'^hook/(?P<key>\w+)/$', csrf_exempt(views.MicrobotHookView.as_view()), name='hook')]
