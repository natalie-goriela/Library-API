from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BooksSerializer


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


class BookModelTests(TestCase):
    def setUp(self):
        self.book = sample_book()

    def test_book_str(self):
        self.assertEqual(str(self.book), "The Great Gatsby (F. Scott Fitzgerald)")

    def test_book_title(self):
        self.assertEqual(str(self.book), "The Great Gatsby (F. Scott Fitzgerald)")

    def test_book_save_with_negative_inventory(self):
        self.book.inventory = -3
        with self.assertRaises(ValidationError):
            self.book.save()

    def test_book_save_with_wrong_cover(self):
        self.book.cover = "other"
        with self.assertRaises(ValidationError):
            self.book.save()

    def test_book_ordering(self):
        book2 = Book.objects.create(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            cover="SOFT",
            inventory=5,
            daily_fee=1.99,
        )
        book3 = Book.objects.create(
            title="Animal Farm",
            author="George Orwell",
            cover="HARD",
            inventory=8,
            daily_fee=2.99,
        )
        books = list(Book.objects.all())
        self.assertEqual(books, [book3, self.book, book2])


class BooksSerializerTests(TestCase):

    def test_book_serializer_create(self):
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 3,
            "daily_fee": 2.5
        }

        serializer = BooksSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_book_serializer_create_with_invalid_inventory(self):
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 1.2,
            "daily_fee": 2.5
        }
        serializer = BooksSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class UnauthorizedBooksViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        response = self.client.get(reverse("books:book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        book1 = sample_book()
        response = self.client.get(reverse("books:book-detail", args=[book1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], book1.title)
        self.assertEqual(response.data["author"], book1.author)

    def test_filter_books_by_title(self):
        book1 = sample_book(title="Book1")
        book2 = sample_book(title="Book2")

        res = self.client.get(reverse("books:book-list"), {"title": "1"})

        serializer1 = BooksSerializer(book1)
        serializer2 = BooksSerializer(book2)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_filter_books_by_author(self):
        book1 = sample_book(author="Author1")
        book2 = sample_book(author="Author2")

        res = self.client.get(reverse("books:book-list"), {"author": "1"})

        serializer1 = BooksSerializer(book1)
        serializer2 = BooksSerializer(book2)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 2.5
        }
        response = self.client.post(reverse("books:book-list"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedBooksViewTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin.user@email.com",
            password="testpass",
            is_staff=False
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 2.5
        }
        response = self.client.post(reverse("books:book-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBooksViewTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin.user@email.com",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 2.5
        }
        response = self.client.post(reverse("books:book-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book(self):
        book = sample_book()
        url = reverse("books:book-detail", args=[book.id])
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 2.6
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book(self):
        book = sample_book()
        url = reverse("books:book-detail", args=[book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

