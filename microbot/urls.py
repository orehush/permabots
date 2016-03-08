from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from microbot import views

urlpatterns = [
    url(r'^telegrambot/(?P<token>[-_:a-zA-Z0-9]+)/$', csrf_exempt(views.WebhookView.as_view()), name='telegrambot'),
]
