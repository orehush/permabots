from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers
from tests import views

router = routers.DefaultRouter()
router.register(r'authors', views.AuthorViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^microbot', include('microbot.urls', namespace="microbot")),
]