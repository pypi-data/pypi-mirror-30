from plugs_payments.signals import valid_ifthen_payment_received
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

# ifthenpay signals
valid_ifthen_payment_received = valid_ifthen_payment_received

# django paypal signals
valid_ipn_received = valid_ipn_received
invalid_ipn_received = invalid_ipn_received
