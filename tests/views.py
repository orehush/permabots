from rest_framework import viewsets
from tests.serializers import AuthorSerializer
from tests.models import Author

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer