from django.core.exceptions import ValidationError
from django.db import models


class Book(models.Model):
    COVER_CHOICES = (
        ("HARD", "H"),
        ("SOFT", "S"),
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=3, decimal_places=2)

    @staticmethod
    def validate_inventory(
            inventory,
            error_to_raise
    ) -> None:
        if not 0 <= inventory or not isinstance(inventory, int):
            raise error_to_raise({
                "inventory": "Inventory must be a positive integer",
            })

    def clean(self):
        Book.validate_inventory(
            inventory=self.inventory,
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
        super(Book, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.author})"

