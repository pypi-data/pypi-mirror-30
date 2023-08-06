from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.apps import apps
from django.dispatch import receiver

from plugs_core.mixins import Timestampable

from .signals import valid_ifthen_payment_received, valid_ipn_received, invalid_ipn_received
from .exceptions import UnavailablePaymentMethod

IFTHENPAY = 'IFTHENPAY'
PAYPAL = 'PAYPAL'

# This is used
PAYMENT_TYPES = [
    (IFTHENPAY, 'IfThenPayment'),
    (PAYPAL, 'PayPal'),
]

# This is not really used right now, soon it will
class PaymentType(Timestampable):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=255)

class BaseOrder(models.Model):
    total = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    payment_type = models.CharField(max_length=24, null=True, choices=PAYMENT_TYPES)
    payment = models.PositiveIntegerField(null=True)
    currency_code = models.CharField(max_length=3, null=True)

    @staticmethod
    def get_payment_model(payment_model_name):
        if payment_model_name == IFTHENPAY:
            return apps.get_model('plugs_payments', 'IfThenPayment')
        if payment_model_name == PAYPAL:
            return
        raise UnavailablePaymentMethod()

    def __init__(self, *args, **kwargs):
        self._check_model_states()
        super().__init__(*args, **kwargs)

    def _check_attr(self, attr):
        if not hasattr(self, attr):
            raise AttributeError('Subclass must have a %s attribute' % attr)

    def _check_model_states(self):
        for attr in ['STATES', 'CREATED', 'IN_PAYMENT', 'PAID']:
            self._check_attr(attr)

    def get_order_items(self):
        raise NotImplementedError

    def get_currency_code(self):
        raise NotImplementedError

    def get_order_total(self):
        total = 0
        for item in self.get_order_items():
            total += item.get_item_price()
        return total

    def set_total(self):
        self.total = self.get_order_total()

    def create_payment(self):
        model = __class__.get_payment_model(self.payment_type)
        # temp hack, ifthen requires payment object before payment
        # paypal does not
        if model:
            payment = model.objects.create(value=self.total)
            self.payment = payment.pk

    def set_payment_type(self):
        if self.payment_type and self.state == self.CREATED:
            self.create_payment()
            self.state = self.IN_PAYMENT

    def save(self, *args, **kwargs):
        self.set_total()
        self.set_payment_type()
        self.currency_code = self.get_currency_code()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class SimpleOrder(BaseOrder):

    def get_order_items(self):
        return [self]

    class Meta:
        abstract = True

@receiver(valid_ifthen_payment_received)
def payment_received(sender, **kwargs):
    app_label, model_name = settings.ORDER_MODEL.split(".")
    model = apps.get_model(app_label, model_name)
    obj = model.objects.get(payment_type=IFTHENPAY, state=model.IN_PAYMENT, payment=sender.pk)
    obj.state = model.PAID
    obj.save()

@receiver(valid_ipn_received)
def ipn_valid_payment_received(sender, **kwargs):
    print('mark the payment as paid')

@receiver(invalid_ipn_received)
def ipn_invalid_payment_received(sender, **kwargs):
    print('do not mark payment as paid, and notify tech staff')
