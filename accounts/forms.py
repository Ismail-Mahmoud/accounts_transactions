from decimal import Decimal
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from .models import Account


class TransactionAdminForm(forms.ModelForm):
    def clean(self) -> dict[str, Any]:
        src_account = Account.objects.get(pk=self.data["src_account"])
        if self.data["src_account"] == self.data["dest_account"]:
            raise ValidationError("Transfer must be done between two different accounts.")
        if src_account.balance < Decimal(self.data["amount"]):
            raise ValidationError("Source account doesn't have enough balance to transfer the specified amount.")
        return super().clean()
