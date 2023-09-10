from django.contrib import admin
from . import models


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "balance"]
    list_per_page = 10
    search_fields = ["name", "id"]


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "src_account", "dest_account", "amount", "created_at"]
    list_per_page = 10
    list_select_related = True
    autocomplete_fields = ["src_account", "dest_account"]
    ordering = ["-created_at"]

