import csv
import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from account_transactions.settings import UPLOADED_FILES

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer, UploadSerializer


class AccountList(ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountDetail(RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransferList(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class UploadViewSet(UpdateAPIView):
    serializer_class = UploadSerializer
    queryset = Account.objects.all()

    def update(self, request: Request):
        accounts_file = request.data.get("accounts_file", None) # type: ignore
        
        try:
            response = self.import_accounts(accounts_file)
        except Exception as e:
            response = Response(
                f"Error while importing accounts: {e}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return response


    def import_accounts(self, file) -> Response:
        if not isinstance(file, InMemoryUploadedFile):
            return Response("No file chosen.", status=status.HTTP_400_BAD_REQUEST)
        
        SUPPORTED_FILE_FORMATS = UPLOADED_FILES["supported_formats"]

        content_type = file.content_type
        file = file.read().decode("utf-8")
        io_file = io.StringIO(file) # type: ignore
        accounts: list[dict] = []

        if content_type == "text/csv":
            accounts = [row for row in csv.DictReader(io_file)]
        elif content_type == "application/json":
            import json
            accounts = json.load(io_file)
        else:
            return Response(
                f"File format not supported. Supported formats are: {SUPPORTED_FILE_FORMATS}",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            db_accounts = [
                Account(
                    id=acc["id"],
                    name=acc["name"],
                    balance=acc["balance"],
                )
                for acc in accounts
            ]
        except KeyError:
            return Response(
                f"Key error. Accounts keys must be {['id', 'name', 'balance']}",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # merge or replace?
        response_data = Account.objects.bulk_create(
            db_accounts,
            update_fields=["balance"],
            update_conflicts=True,
            unique_fields=["id"], # type: ignore
        )
        
        return Response(
            # f"{len(db_accounts)} Accounts imported successfully.",
            [AccountSerializer(instance=acc).data for acc in response_data],
            status=status.HTTP_200_OK
        )
