from rest_framework.exceptions import APIException

class UnavailablePaymentMethod(APIException):
     status_code = 400
     default_detail = 'Payment method not available'
     default_code = 'bad_request'
