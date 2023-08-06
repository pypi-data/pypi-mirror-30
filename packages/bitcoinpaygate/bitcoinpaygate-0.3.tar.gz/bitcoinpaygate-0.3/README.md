# Bitcoinpaygate API client for Python

## Usage

### Installation
```bash
$ pip install bitcoinpaygate
```

### Creating Client object

First of all, you should instantiate Client object:

```python
from bitcoinpaygate import Client, NewPaymentRequest, PaymentStatus

API_KEY_NAME = 'some_key'               # Your API key name 
API_KEY_PASSWORD = 'b32ab...'           # Your API key password
API_HOST = 'http://example.com/api/v2/' # URL of BitcoinPayGate API
client = Client(
    api_key_name=API_KEY_NAME,
    api_key_password=API_KEY_PASSWORD,
    api_host=API_HOST)
```

### Creating new payment request

To create new payment request:

```python
new_payment = NewPaymentRequest(
    amount=0.04,
    currency='USD',
    notificationUrl='https://example.com/notify',
    message='test',
    merchantTransactionId='2015-03-10/123/1'         # An id of the transaction in your system
)

payment = client.process(new_payment)

# or use a shorthand:

payment = client.new_payment(
    amount=0.04,
    currency='USD',
    notificationUrl='https://example.com/notify',
    message='test',
    merchantTransactionId='2015-03-10/123/1'
)

transaction_id = payment.transactionId

```

When your new payment request is invalid, e.g. no HTTPS notification URL has been set, the client will throw an exception `InvalidRequest`.

### Checking payment receipt

To check current payment receipt:

```python
receipt = client.check_payment_receipt(transaction_id)

if (receipt.status == PaymentStatus.NEW):
	print(receipt.status)
```

### Requesting payment notification

To request payment notification:

```python
client.request_payment_notification(transaction_id)
```

### Development

If you want to develop next features in the client, you should install dependencies first:

```bash
$ pip install -r requirements.txt
```
To run the tests:

First start mockup server:

```bash
$ make mock_server
```
and then execute the tests:

```bash
$ make test
```

### Deployment

Create the packages (stored in /dist directory):
```bash
$ make dist
```

... then upload them to PyPI (the Python Package Index):
```bash
$ make upload
```
