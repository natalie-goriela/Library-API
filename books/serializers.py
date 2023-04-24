from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book


class BooksSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BooksSerializer, self).validate(attrs=attrs)
        Book.validate_inventory(
            attrs["inventory"],
            ValidationError
        )
        return data

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BooksBriefSerializer(BooksSerializer):
    class Meta:
        model = Book
        fields = ("title", "author")
