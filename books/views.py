from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, AllowAny

from books.models import Book

from books.serializers import BooksSerializer


class BooksPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    pagination_class = BooksPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return (AllowAny(),)
        return (IsAdminUser(),)

    def get_queryset(self):
        """Retrieve the movies with filters"""
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset.distinct()

