from django.contrib import admin
from django.db import transaction

from .models import Account, Transaction
from .forms import TransactionAdminForm


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "balance"]
    list_per_page = 10
    search_fields = ["name", "id"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "src_account", "dest_account", "amount", "created_at"]
    list_per_page = 10
    list_select_related = True
    autocomplete_fields = ["src_account", "dest_account"]
    ordering = ["-created_at"]

    form = TransactionAdminForm

    def save_model(self, request, obj, form, change):
        self.update_accounts(obj)
        super().save_model(request, obj, form, change)

    def update_accounts(self, obj: Transaction):
        with transaction.atomic():
            obj.src_account.balance -= obj.amount
            obj.dest_account.balance += obj.amount
            obj.src_account.save()
            obj.dest_account.save()
