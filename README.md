# Accounts Transactions
A Django app that handles balance transfers between two accounts.
It supports importing a list of accounts with opening balances from CSV or JSON files.

# Requirements
Python 3.10+

# Installation
[Optional] Create a new virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip3 install -r requirements.txt
```

Alternatively, you can run the app inside a docker container:
```bash
docker build -t <IMAGE_NAME> .
docker run --name <CONTAINER_NAME> -itd -p 8000:8000 <IMAGE_NAME>
```

# Database Models
## Account

| Field |   Type    |  Description  |   Required    |   Default      |
| ----  |   ----    |   --------    |   --------    |   ------       |
|  id   |   UUID    |   Account ID  |       NO      | Auto-generated |
|  name |   STRING  |  Account Name |       YES     |       -        |
|balance|   NUMBER  |Account Balance|       NO      |   0.00         |

## Transaction
| Field |   Type    |  Description  |   Required    |   Default     |
| ----  |   ----    |   --------    |   --------    |   ------      |
|  id   |   UUID    |   Transaction ID  |       NO      | Auto-generated |
|  src_account  |   UUID  | Source Account ID      |       YES      | - |
|  dest_account |   UUID  | Destination Account ID  |       YES     | - |
|   amount      | NUMBER  | Amount to be transferred |       YES     | - |
|   created_at  | DATETIME  | Timestamp at which transaction is created |NO| Auto-generated |

# Available Endpoints

Import this [file](./openapi.yaml) into any API documentation tool (like [Swagger](https://editor.swagger.io/) for example) for better readability

### /accounts/

#### GET
##### Description:

List all accounts

##### Responses

| Code  | Description |
| ----  | ----------- |
| 200   | Successful operation |

#### POST
##### Description:

Create a new account

##### Request Body

`Account` object

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful account creation |
| 400 | Invalid account data |

### /accounts/{id}/

#### GET
##### Description:

Get account by ID

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful operation |
| 404 | Account not found |

### /accounts/transfer/

#### POST
##### Description:

Transfer balance between two accounts

##### Request Body

`Transaction` object

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successful transaction |
| 400 | Invalid transaction  |
|     | Transferred amount is not positive |
|     | Source or destination account not found |
|     | Source and destination accounts are the same |
|     | Transferred amount exceeds source account balance |

### /accounts/import/

#### PUT
##### Description:

Import accounts from uploaded file and save them into the `Accounts` database.

Note that if an account already exists in the database, it will be updated using values in the file.

Supported file formats are CSV and JSON.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful import |
| 400 | Unsupported file format / Invalid data |
| 500 | Internal server error |


# Usage
### Browsable API
Using Django REST Framework, you'll be able to browse the API and submit requests in a convenient way.

Run the following commands to perform database migrations and start the server (skip if you're running a docker container):
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

Go to http://localhost:8000/accounts/import/ to import accounts from CSV/JSON file (check [samples](./samples/)).

Once the accounts are imported successfully, you'll be able to view imported accounts and perform transactions between them as follows:
- List and create new accounts: http://localhost:8000/accounts/
- Get account by ID: http://localhost:8000/accounts/{id}/
- Transfer balance between two accounts: http://localhost:8000/accounts/transfer/

### Admin Site
You can perform generic CRUD operations by accessing the admin site interface, which comes out of the box with Django.

First, you need to create a superuser:
```bash
python3 manage.py createsuperuser
```
If running a docker container:
```bash
docker exec -it <CONTAINER_NAME> python3 manage.py createsuperuser
```

Then, go to http://localhost:8000/admin/ and login with your superuser credentials.

# Testing
To run tests and get coverage report, run the following command:
```bash
pytest --cov=accounts/
```
If running a docker container:
```bash
docker exec -it <CONTAINER_NAME> pytest --cov=accounts/
```
