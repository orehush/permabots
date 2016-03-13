from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers
from tests import views
from microbot import views as micro_views
from rest_framework.authtoken import views as rdf_views

router = routers.DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'books', views.BookViewSet)

urlpatterns = [
    url(r'^api-token-auth/', rdf_views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^microapi/bots/$', micro_views.BotList.as_view()),
    url(r'^microapi/bots/(?P<pk>[0-9]+)/$', micro_views.BotDetail.as_view()),
    url(r'^microapi/bots/(?P<bot_pk>[0-9]+)/env/$', micro_views.EnvironmentVarList.as_view()),
    url(r'^microapi/bots/(?P<bot_pk>[0-9]+)/env/(?P<pk>[0-9]+)/$', micro_views.EnvironmentVarDetail.as_view()),
    url(r'^microbot', include('microbot.urls', namespace="microbot")),
]