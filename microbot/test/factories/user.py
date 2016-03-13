# coding=utf-8
from factory import DjangoModelFactory, Sequence, PostGenerationMethodCall
from django.conf import settings

class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    email = Sequence(lambda n: 'user%d@test.com' % n)
    username = Sequence(lambda n: 'user%d' % n)
    password = PostGenerationMethodCall('set_password', 'adm1n')

    is_superuser = False
    is_staff = False
    is_active = True