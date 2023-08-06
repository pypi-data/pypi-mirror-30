from __future__ import print_function

import json
import requests
from decimal import Decimal

from .utils import property_not_empty
from .communication import (
    NewPaymentRequest,
    NewPaymentResponse,
    PaymentReceipt,
    RequestNotificationResponse
)

class PaymentStatus(object):
    NEW       = 'NEW'
    UNDERPAID = 'UNDERPAID'
    CONFIRMED = 'CONFIRMED'
    COMPLETED = 'COMPLETED'
    EXPIRED   = 'EXPIRED'
    INVALID   = 'INVALID'

class InvalidRequest(Exception):

    def __init__(self, response):
        self.original_response = response
        self.code = response.status_code
        self.message = response.text


class Client(object):

    DEFAULT_API_HOST = 'https://testing.process9100.com/api/v2/'
    NEW_PAYMENT = 'payments/new'
    PAYMENT_STATUS = 'payments/{payment_id}'
    RESEND_NOTIFICATION = 'payments/notify/{payment_id}'

    _api_host = None
    @property
    def api_host(self):
        return self._api_host

    @api_host.setter
    @property_not_empty
    def api_host(self, value):
        if not value.endswith('/'):
            value = value + '/'
        self._api_host = value

    _api_key_name = None
    @property
    def api_key_name(self):
        return self._api_key_name

    @api_key_name.setter
    @property_not_empty
    def api_key_name(self, value):
        self._api_key_name = value

    _api_key_password = None
    @property
    def api_key_password(self):
        return self._api_key_password

    @api_key_password.setter
    @property_not_empty
    def api_key_password(self, value):
        self._api_key_password = value

    def __init__(self, api_key_name, api_key_password, api_host = None):
        self.api_key_name = api_key_name
        self.api_key_password = api_key_password
        if api_host:
            self.api_host = api_host
        else:
            self.api_host = self.DEFAULT_API_HOST

    def process(self, new_payment_request):
        data = new_payment_request.to_dict()
        response = self.post_request(self.NEW_PAYMENT, **data)
        json_str = response.text
        parsed_json = json.loads(json_str, parse_float=Decimal)
        return NewPaymentResponse(**parsed_json)


    # SHORTCUTS:
    def new_payment(self, **kwargs):
        return self.process(NewPaymentRequest(**kwargs))

    def check_payment_receipt(self, transaction_id):
        response = self.get_request(self.PAYMENT_STATUS, payment_id=transaction_id)
        json_str = response.text
        parsed_json = json.loads(json_str, parse_float=Decimal)
        return PaymentReceipt(**parsed_json)

    def request_payment_notification(self, transaction_id):
        response = self.get_request(self.RESEND_NOTIFICATION, payment_id=transaction_id)
        json_str = response.text
        parsed_json = json.loads(json_str, parse_float=Decimal)
        return RequestNotificationResponse(**parsed_json)


    # REQUESTS:
    def post_request(self, endpoint, **kwargs):
        url = self.api_host + endpoint
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(kwargs), auth=(self.api_key_name, self.api_key_password))
        if response.status_code != 200:
            raise InvalidRequest(response)
        return response

    def get_request(self, endpoint, **url_params):
        url = (self.api_host + endpoint).format(**url_params)
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, auth=(self.api_key_name, self.api_key_password))
        if response.status_code != 200:
            raise InvalidRequest(response)
        return response

