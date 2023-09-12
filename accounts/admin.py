from django.contrib import admin
from django.db import transaction
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource

from account_transactions.settings import UPLOADED_FILES

from .forms import TransactionAdminForm
from .models import Account, Transaction


class AccountResource(ModelResource):
    id = Field(attribute="id")
    name = Field(attribute="name")
    balance = Field(attribute="balance")
    
    class Meta:
        model = Account


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin):
    list_display = ["id", "name", "balance"]
    list_per_page = 10
    search_fields = ["name", "id"]

    resource_class = AccountResource


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
