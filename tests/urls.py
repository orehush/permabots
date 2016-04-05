from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers
from tests import views
from rest_framework.authtoken import views as rdf_views

router = routers.DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'books', views.BookViewSet)

urlpatterns = [
    url(r'^api-token-auth/', rdf_views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^microbot/api/', include('microbot.urls_api', namespace="api")),
    url(r'^process/', include('microbot.urls_processing', namespace="microbot")),
]