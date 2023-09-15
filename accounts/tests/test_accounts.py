from uuid import uuid4

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response

from account_transactions.settings import REST_FRAMEWORK
from accounts.models import Account


@pytest.mark.django_db
class TestCreateAccount:
    def test_valid_account_201(self, create_account):
        account = {
            "name": "Ali"
        }
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_invalid_uuid_400(self, create_account):
        account = {
            "id": "string",
            "name": "Ali",
            "balance": 50,
        }
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_id_400(self, create_account):
        id = uuid4()
        account = {
            "id": id,
            "name": "Ali",
        }
        create_account(account)
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_name_400(self, create_account):
        account = {}
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_invalid_name_empty_400(self, create_account):
        account = {
            "name": "",
            "balance": 50,
        }
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_balance_negative_400(self, create_account):
        account = {
            "name": "Ali",
            "balance": -1,
        }
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_balance_max_digits_400(self, create_account):
        account = {
            "name": "Ali",
            "balance": 9999999999999,
        }
        response: Response = create_account(account)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestGetAccount:
    def test_existing_account_200(self, get_account):
        account = baker.make(Account)
        response: Response = get_account(account.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": str(account.id),
            "name": account.name,
            "balance": account.balance,
        }

    def test_non_existing_account_404(self, get_account):
        response: Response = get_account("ffff")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListAccounts:
    NUM_ACCOUNTS = 42
    
    def test_list_accounts_200(self, api_client, list_accounts):
        
        self.NUM_ACCOUNTS = 1000

        accounts = baker.make(Account, _quantity=self.NUM_ACCOUNTS, _bulk_create=True)
        response: Response = list_accounts()

        assert response.status_code == status.HTTP_200_OK
        
        response_accounts = (
            self.concat_pagination_results(api_client, response) if "DEFAULT_PAGINATION_CLASS" in REST_FRAMEWORK
            else response.data
        )

        assert len(accounts) == len(response_accounts) # type: ignore

        accounts.sort(key=lambda acc: str(acc.id))
        response_accounts.sort(key=lambda acc: acc["id"])
        
        for acc, res_acc in zip(accounts, response_accounts): # type: ignore
            assert res_acc == {
                "id": str(acc.id),
                "name": acc.name,
                "balance": acc.balance,
            }

    def concat_pagination_results(self, api_client, response: Response) -> list[dict]:
        assert response.data.get("count", -1) == self.NUM_ACCOUNTS
        accounts = []
        next_ = None
        while True:
            accounts += response.data.get("results", [])
            next_ = response.data.get("next")
            if not next_:
                break
            response = api_client.get(next_)
        return accounts


@pytest.mark.django_db(transaction=True)
class TestTransferBalance:
    def test_successful_transaction_200(self, create_transaction):
        SRC_BALANCE, DEST_BALANCE, TRANSFERED_AMOUNT = 4000, 1000, 500
        src_account = baker.make(Account, balance=SRC_BALANCE)
        dest_account = baker.make(Account, balance=DEST_BALANCE)

        transaction = {
            "src_account": src_account.id,
            "dest_account": dest_account.id,
            "amount": TRANSFERED_AMOUNT,
        }
        
        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_201_CREATED

        new_src_balance = Account.objects.get(pk=src_account.id).balance
        new_dest_balance = Account.objects.get(pk=dest_account.id).balance

        assert new_src_balance == SRC_BALANCE - TRANSFERED_AMOUNT
        assert new_dest_balance == DEST_BALANCE + TRANSFERED_AMOUNT

    def test_non_existing_accounts_400(self, create_transaction):
        transaction = {
            "src_account": uuid4(),
            "dest_account": uuid4(),
            "amount": 100,
        }
        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_transfered_amount_400(self, create_transaction):
        src_account = baker.make(Account)
        dest_account = baker.make(Account)
        transaction = {
            "src_account": src_account.id,
            "dest_account": dest_account.id,
        }
        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_positive_transfered_amount_400(self, create_transaction):
        SRC_BALANCE, DEST_BALANCE, TRANSFERED_AMOUNT = 4000, 1000, 0
        src_account = baker.make(Account, balance=SRC_BALANCE)
        dest_account = baker.make(Account, balance=DEST_BALANCE)

        transaction = {
            "src_account": src_account.id,
            "dest_account": dest_account.id,
            "amount": TRANSFERED_AMOUNT,
        }

        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_transfered_amount_exceeds_src_balance_400(self, create_transaction):
        SRC_BALANCE, DEST_BALANCE, TRANSFERED_AMOUNT = 4000, 1000, 9999
        src_account = baker.make(Account, balance=SRC_BALANCE)
        dest_account = baker.make(Account, balance=DEST_BALANCE)

        transaction = {
            "src_account": src_account.id,
            "dest_account": dest_account.id,
            "amount": TRANSFERED_AMOUNT,
        }

        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_same_src_and_dest_accounts_400(self, create_transaction):
        account = baker.make(Account, balance=1000)
        transaction = {
            "src_account": account.id,
            "dest_account": account.id,
            "amount": 1,
        }
        response: Response = create_transaction(transaction)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestImportAccounts:
    def test_successful_import_csv_200(self, upload_file):
        file = SimpleUploadedFile(
            name="accounts.csv",
            content=b"""id,name,balance
02ec6d00-2aff-4f76-9d34-8fc99084eea1,Demott Lally,942.11
364d1e1e-cf8c-437c-a74b-271960d7576e,Rachel Isles,558.93
d0610e17-f072-4a94-8ab8-238740ed3fe4,Cacilie Stovold,208.47
84d0b016-d15c-41bd-b7f1-1bbdc5389d7a,Toddie Eingerfield,299.29
30f015f7-529c-4ecc-9a96-422bdd976089,Davina Treadgall,386.25
""",
            content_type="text/csv"
        )

        response: Response = upload_file(file)
        assert response.status_code == status.HTTP_200_OK

    def test_successful_import_json_200(self, upload_file):
        file = SimpleUploadedFile(
            name="accounts.json",
            content=b"""[
                {
                    "id": "6e17b81c-0a0c-414d-8514-eb19633753b5",
                    "name": "Tommy Veldens",
                    "balance": 296.32
                },
                {
                    "id": "85e6f560-7eb5-4f17-b933-85c7a1cce34d",
                    "name": "Gavin Klehyn",
                    "balance": 709.29
                },
                {
                    "id": "a408e676-c967-42fd-8259-7e73654dcbe6",
                    "name": "Bianca Coste",
                    "balance": 433.77
                },
                {
                    "id": "3615356d-5bdb-4280-b760-80a4b7d4f88e",
                    "name": "Zebedee Gillibrand",
                    "balance": 118.4
                },
                {
                    "id": "7b48b558-2091-4623-b8ba-128d783831b3",
                    "name": "Barnebas Towse",
                    "balance": 210.08
                }
            ]""",
            content_type="application/json"
        )

        response: Response = upload_file(file)

        response_accounts = response.data
        database_accounts = Account.objects.all()
            
        assert response.status_code == status.HTTP_200_OK
        
        for db_acc, res_acc in zip(database_accounts, response_accounts):
            assert res_acc == {
                "id": str(db_acc.id),
                "name": db_acc.name,
                "balance": db_acc.balance,
            }

    def test_unsupported_format_400(self, upload_file):
        file = SimpleUploadedFile(
            name="accounts.txt",
            content=b"asdf",
            content_type="text/plain"
        )

        response: Response = upload_file(file)
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_no_file_chosen_400(self, upload_file):
        file = ""
        response: Response = upload_file(file)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_account_key_error_400(self, upload_file):
        file = SimpleUploadedFile(
            name="accounts.csv",
            content=b"""ID,FULL_NAME,BALANCE
cc26b56c-36f6-41f1-b689-d1d5065b95af,John Doe,797.22
""",
            content_type="text/csv"
        )

        response: Response = upload_file(file)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
