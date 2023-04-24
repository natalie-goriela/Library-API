import datetime

from django.db import transaction
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.serializers import (
    BorrowingsSerializer,
    BorrowingsListSerializer,
    BorrowingsDetailSerializer,
    BorrowingsUpdateSerializer
)
from borrowings.models import Borrowing


class BorrowingsPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BorrowingsViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingsSerializer
    pagination_class = BorrowingsPagination

    def get_queryset(self):
        is_active_param = self.request.query_params.get("is_active", None)
        user_param = self.request.query_params.get("user", None)

        queryset = Borrowing.objects.all()

        if self.request.user.is_staff:

            if is_active_param:
                queryset = queryset.filter(actual_return_date__isnull=True)

            if user_param:
                queryset = queryset.filter(user__id=int(user_param))

            return queryset

        queryset = Borrowing.objects.filter(user=self.request.user)

        if is_active_param:
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingsListSerializer
        if self.action == "retrieve":
            return BorrowingsDetailSerializer
        if self.action == "update":
            return BorrowingsUpdateSerializer
        return BorrowingsSerializer

    @transaction.atomic()
    @action(
        methods=["PUT"],
        detail=True,
        url_path="return",
        serializer_class=None
    )
    def return_borrowing(self, request: Request, pk: int = None) -> Response:

        borrowing = self.get_object()

        if borrowing.actual_return_date:
            raise ValidationError("The book has already been returned")
        if self.request.user != borrowing.user:
            raise ValidationError("You have no access to this borrowing")

        borrowing.actual_return_date = datetime.date.today()
        borrowing.save()
        book = borrowing.book
        book.inventory += 1
        book.save()
        
        return Response({"status": "Returned"}, status=status.HTTP_200_OK)
