from rest_framework import viewsets, filters
from tests.serializers import AuthorSerializer, BookSerializer
from tests.models import Author, Book
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authors to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'id')
    
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)