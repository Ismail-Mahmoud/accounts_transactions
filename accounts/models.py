from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from uuid import uuid4


DECIMAL_MAX_DIGITS = 10
DECIMAL_PLACES = 2


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=DECIMAL_MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        default=Decimal(0),
        validators=[MinValueValidator(0)],
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.balance})"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    src_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="+")
    dest_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="+")
    amount = models.DecimalField(
        max_digits=DECIMAL_MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
