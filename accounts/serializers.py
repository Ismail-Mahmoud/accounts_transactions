from django.db import transaction
from rest_framework import serializers
from .models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "balance"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "src_account", "dest_account", "amount", "created_at"]

    def validate(self, data):
        if data["src_account"] == data["dest_account"]:
            raise serializers.ValidationError("Transfer must be done between two different accounts.")
        if data["src_account"].balance < data["amount"]:
            raise serializers.ValidationError("Source account doesn't have enough balance to transfer the specified amount.")
        return data

    def save(self, **kwargs):
        def transfer():
            src_account: Account = self.validated_data["src_account"] # type: ignore
            dest_account: Account = self.validated_data["dest_account"] # type: ignore
            amount = self.validated_data["amount"] # type: ignore

            src_account.balance -= amount
            dest_account.balance += amount
            
            src_account.save()
            dest_account.save()
        
        with transaction.atomic():    
            transfer()
            return super().save(**kwargs)
