from rest_framework import viewsets, filters
from tests.serializers import AuthorSerializer
from tests.models import Author

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authors to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'id')