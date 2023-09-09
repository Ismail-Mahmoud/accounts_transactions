from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .models import Account
from .serializers import AccountSerializer, TransactionSerializer


def welcome(reauest: HttpRequest):
    return HttpResponse("Hello World!")


class AccountInfo(APIView):
    def get(self, request: Request, id):
        """Get account by ID"""
        account = get_object_or_404(Account, pk=id)
        serializer = AccountSerializer(instance=account)
        return Response(serializer.data)
    
    def patch(self, request: Request, id):
        """Update account by ID"""
        account = get_object_or_404(Account, pk=id)
        serializer = AccountSerializer(instance=account, data=request.data, partial=True) # type: ignore
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=account, validated_data=request.data)
        return Response(data=serializer.data)


class AccountsList(APIView):
    def get(self, request: Request):
        """List all accounts"""
        queryset = Account.objects.all()
        serializer = AccountSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request: Request):
        """Create new account"""
        serializer = AccountSerializer(data=request.data) # type: ignore
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    


# class ImportAccounts(APIView):
#     def post(self, request: Request):
#         pass


class TransferBalance(APIView):
    def post(self, request: Request):
        """Create new transaction"""
        serializer = TransactionSerializer(data=request.data) # type: ignore
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
