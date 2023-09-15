import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_account(api_client):
    def send_request(account):
        return api_client.post("/accounts/", account)
    return send_request

@pytest.fixture
def get_account(api_client):
    def send_request(id):
        return api_client.get(f"/accounts/{id}/")
    return send_request

@pytest.fixture
def list_accounts(api_client):
    def send_request():
        return api_client.get(f"/accounts/")
    return send_request

@pytest.fixture
def create_transaction(api_client):
    def send_request(transaction):
        return api_client.post("/accounts/transfer/", transaction)
    return send_request

@pytest.fixture
def upload_file(api_client):
    def send_request(file):
        return api_client.put("/accounts/import/", {"accounts_file": file})
    return send_request
