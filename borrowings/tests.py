import uuid
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.core.exceptions import ValidationError as VE
from rest_framework.test import APIClient
from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingsSerializer,
    BorrowingsUpdateSerializer,
)


def sample_book(**params):
    defaults = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "cover": "HARD",
        "inventory": 3,
        "daily_fee": 2.5
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": f"{uuid.uuid4()}@test.com",
        "password": "test_password",
        "first_name": "Test",
        "last_name": "User"
    }
    defaults.update(params)
    return get_user_model().objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": (date.today() + timedelta(days=14)),
        "book": sample_book(),
        "user": sample_user()
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.book = sample_book()
        self.user = sample_user()
        self.borrowing = sample_borrowing(book=self.book, user=self.user)

    def test_str(self):
        self.assertEqual(str(self.borrowing), str(date.today()))

    def test_borrowing_backdating(self):
        with self.assertRaises(VE):
            Borrowing.objects.create(
                borrow_date="1999-03-07",
                expected_return_date=(date.today() + timedelta(days=14)),
                book=self.book,
                user=self.user,
            )

    def test_expected_return_date_earlier_than_borrow_date(self):
        with self.assertRaises(VE):
            Borrowing.objects.create(
                borrow_date=date.today(),
                expected_return_date=(date.today() + timedelta(days=-5)),
                book=self.book,
                user=self.user,
            )

    def test_return_date_earlier_than_borrow_date(self):
        with self.assertRaises(VE):
            Borrowing.objects.create(
                borrow_date=date.today(),
                expected_return_date=(date.today() + timedelta(days=14)),
                actual_return_date=(date.today() + timedelta(days=-5)),
                book=self.book,
                user=self.user,
            )


class BorrowingsSerializerTests(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.book = sample_book()

    def test_serializer_is_valid(self):
        data = {
            "borrow_date": date.today(),
            "expected_return_date": (date.today() + timedelta(days=14)),
            "book": self.book.id,
            "user": self.user.id
        }
        serializer = BorrowingsSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_serializer_create_with_invalid_borrow_date(self):
        data = {
            "borrow_date": "2022-04-30",
            "expected_return_date": (date.today() + timedelta(days=14)),
            "book": self.book.id,
            "user": self.user.id
        }
        serializer = BorrowingsSerializer(data=data)

        self.assertFalse(serializer.is_valid())


class BorrowingsUpdateSerializerTests(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.book = sample_book()
        self.borrowing = sample_borrowing(book=self.book, user=self.user)

    def test_serializer_update_with_valid_return_date(self):
        data = {
            "actual_return_date": (date.today() + timedelta(days=14)),
        }
        serializer = BorrowingsUpdateSerializer(instance=self.borrowing, data=data)

        self.assertTrue(serializer.is_valid())

    def test_serializer_update_with_invalid_return_date(self):
        data = {
            "actual_return_date": "2022-03-03",
        }
        serializer = BorrowingsUpdateSerializer(instance=self.borrowing, data=data)

        self.assertFalse(serializer.is_valid())


class UnauthorizedBorrowingsViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_borrowings_list(self):
        response = self.client.get(reverse("borrowings:borrowing-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedBorrowingsViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = sample_user(is_staff=True)
        self.user = sample_user()
        self.admin_borrowing = sample_borrowing(user=self.admin_user)
        self.borrowing = sample_borrowing(user=self.user)

        self.client.force_authenticate(self.user)

    def test_user_list_borrowings(self):
        user_borrowings = Borrowing.objects.filter(user=self.user)
        response = self.client.get(reverse("borrowings:borrowing-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), len(user_borrowings))

    def test_create_borrowing(self):
        book = sample_book()
        data = {
            "borrow_date": date.today(),
            "expected_return_date": (date.today() + timedelta(days=14)),
            "book": book.id,
            "user": self.user.id
        }
        response = self.client.post(reverse("borrowings:borrowing-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_borrowing(self):
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        data = {
            "actual_return_date": date.today(),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_borrowings(self):
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminBorrowingsViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = sample_user(is_staff=True)
        self.user = sample_user()
        self.admin_borrowing = sample_borrowing(user=self.admin_user)
        self.borrowing = sample_borrowing(user=self.user)

        self.client.force_authenticate(self.admin_user)

    def test_admin_list_borrowings(self):
        borrowings = Borrowing.objects.all()
        response = self.client.get(reverse("borrowings:borrowing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), len(borrowings))

