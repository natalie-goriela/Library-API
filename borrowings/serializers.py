from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BooksSerializer, BooksBriefSerializer
from borrowings.models import Borrowing
from borrowings.telegram_utils import send_telegram_notification


class BorrowingsSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(BorrowingsSerializer, self).validate(attrs=attrs)
        Borrowing.validate_borrow_date(
            attrs["borrow_date"],
            ValidationError
        )
        Borrowing.validate_expected_return_date(
            attrs["borrow_date"],
            attrs["expected_return_date"],
            ValidationError
        )
        return data

    def create(self, validated_data):
        book = validated_data.pop("book")
        book = Book.objects.get(id=book.id)
        if book.inventory == 0:
            raise ValidationError(
                "All copies of this book are currently in hand. "
                "Please choose another one."
            )
        book.inventory -= 1
        book.save()
        borrowing = Borrowing.objects.create(book=book, **validated_data)
        send_telegram_notification(
            borrowing.id,
            borrowing.borrow_date,
            borrowing.expected_return_date,
            borrowing.book,
            borrowing.user.email,
        )
        return borrowing

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )


class BorrowingsListSerializer(BorrowingsSerializer):
    book = BooksBriefSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingsDetailSerializer(BorrowingsListSerializer):
    book = BooksSerializer(many=False, read_only=True)


class BorrowingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "actual_return_date",
        )

    def validate(self, attrs):
        data = super(BorrowingsUpdateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_actual_return_date(
            self.instance.borrow_date,
            attrs["actual_return_date"],
            ValidationError
        )
        return data

    def update(self, instance, validated_data):
        if instance.actual_return_date:
            raise ValidationError("The actual return date has already been set")
        book = instance.book
        book.inventory += 1
        book.save()
        instance.actual_return_date = validated_data.get(
            "actual_return_date"
        )
        instance.save()
        return instance
