from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from uuid import uuid4


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal(0),
        validators=[MinValueValidator(0)],
    )
