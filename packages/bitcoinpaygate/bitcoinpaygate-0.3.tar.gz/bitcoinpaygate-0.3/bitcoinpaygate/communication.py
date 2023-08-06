from __future__ import print_function

from .utils import property_not_empty

class Printable(object):
    def __str__(self):
        fields = self.__dict__.iteritems()
        values = '\n  '.join(["%s=%s" % (k, v) for k, v in fields])
        cls_name = self.__class__.__name__
        return "%s:\n  %s" % (cls_name, values)

class FromDict(object):

    def from_dict(self, dictionary):
        for k, v in dictionary.iteritems():
            setattr(self, k, v)

class ToDict(object):
    fields = []

    def to_dict(self):
        return {k: getattr(self, k) for k in self.fields if getattr(self, k) is not None}


class NewPaymentRequest(ToDict):

    fields = [
        'amount',
        'currency',
        'notificationUrl',
        'message',
        'merchantTransactionId'
    ]

    # AMOUNT
    _amount = None
    @property
    def amount(self):
        return self._amount

    @amount.setter
    @property_not_empty
    def amount(self, value):
        self._amount = value


    # CURRENCY
    _currency = None
    @property
    def currency(self):
        return self._currency

    @currency.setter
    @property_not_empty
    def currency(self, value):
        self._currency = value

    # NOTIFICATION URL
    _notificationUrl = None
    @property
    def notificationUrl(self):
        return self._notificationUrl

    @notificationUrl.setter
    @property_not_empty
    def notificationUrl(self, value):
        self._notificationUrl = value

    # MESSAGE
    _message = None
    @property
    def message(self):
        return self._message

    @message.setter
    @property_not_empty
    def message(self, value):
        self._message = value

    # MERCHANT TRANSACTION ID
    _merchantTransactionId = None
    @property
    def merchantTransactionId(self):
        return self._message

    @merchantTransactionId.setter
    @property_not_empty
    def merchantTransactionId(self, value):
        self._merchantTransactionId = value

    def __init__(
        self,
        amount,
        currency,
        notificationUrl,
        message,
        merchantTransactionId):

        self.amount = amount
        self.currency = currency
        self.notificationUrl = notificationUrl
        self.message = message
        self.merchantTransactionId = merchantTransactionId

class NewPaymentResponse(FromDict, Printable):

    def __init__(self, **kwargs):
        self.from_dict(kwargs)

class PaymentReceipt(FromDict, Printable):

    def __init__(self, **kwargs):
        self.from_dict(kwargs)

class RequestNotificationResponse(FromDict, Printable):

    def __init__(self, **kwargs):
        self.from_dict(kwargs)
