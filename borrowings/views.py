from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
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
