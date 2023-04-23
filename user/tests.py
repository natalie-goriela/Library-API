from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import UserSerializer, AuthTokenSerializer


class UserModelTests(TestCase):
    def test_user_str(self):
        user = get_user_model().objects.create_user(
            email="test@email.com",
            password="test_password",
            first_name="First",
            last_name="Last",
        )

        self.assertEqual(user.email, "test@email.com")
        self.assertEqual(user.first_name, "First")
        self.assertEqual(user.last_name, "Last")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("test_password"))
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")


class UserSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@email.com",
            password="test_password",
            first_name="First",
            last_name="Last",
        )
        self.serializer = UserSerializer(instance=self.user)

    def test_user_serializer_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "email", "first_name", "last_name", "is_staff"},
        )

    def test_user_serializer_create(self):
        data = {
            "email": "test@test.com",
            "password": "password",
            "is_staff": False,
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.check_password("password"))

    def test_user_serializer_update(self):
        data = {"password": "new_password"}
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password("new_password"))


class AuthTokenSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password",
            first_name="Test",
            last_name="User",
        )
        self.client = APIClient()

    def test_auth_token_serializer_fields(self):
        data = {"email": "test@test.com", "password": "test_password"}
        serializer = AuthTokenSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_auth_token_serializer_invalid_credentials(self):
        data = {"email": "test@test.com", "password": "invalid_password"}
        serializer = AuthTokenSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_auth_token_serializer_missing_fields(self):
        data = {"email": "test@test.com"}
        serializer = AuthTokenSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)


class CreateUserViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:create")

    def test_create_user(self):
        data = {
            "email": "test@test.com",
            "password": "password",
            "first_name": "First",
            "last_name": "Last",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticatedManageUserViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            first_name="First",
            last_name="Last",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user:manage")

    def test_user_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@test.com")

    def test_user_update_view(self):
        data = {"first_name": "New"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "New")


class UnauthenticatedManageUserViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            first_name="First",
            last_name="Last",
        )
        self.client = APIClient()
        self.url = reverse("user:manage")

    def test_user_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
