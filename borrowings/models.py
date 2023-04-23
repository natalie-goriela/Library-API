import datetime

from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def validate_borrow_date(
            borrow_date,
            error_to_raise
    ) -> None:
        if borrow_date < datetime.date.today():
            raise error_to_raise({
                "borrow_date": "The borrowing cannot be backdated",
            })

    @staticmethod
    def validate_expected_return_date(
            borrow_date,
            expected_return_date,
            error_to_raise
    ) -> None:
        if expected_return_date < borrow_date:
            raise error_to_raise({
                "expected_return_date": "Return date cannot be earlier than the borrow date",
            })

    @staticmethod
    def validate_actual_return_date(
            borrow_date,
            actual_return_date,
            error_to_raise
    ) -> None:
        if actual_return_date and actual_return_date < borrow_date:
            raise error_to_raise({
                "actual_return_date": "Return date cannot be earlier than the borrow date",
            })

    def clean(self):
        Borrowing.validate_borrow_date(
            borrow_date=self.borrow_date,
            error_to_raise=ValidationError
        )
        Borrowing.validate_expected_return_date(
            borrow_date=self.borrow_date,
            expected_return_date=self.expected_return_date,
            error_to_raise=ValidationError
        )
        Borrowing.validate_actual_return_date(
            borrow_date=self.borrow_date,
            actual_return_date=self.actual_return_date,
            error_to_raise=ValidationError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"{self.borrow_date}"

