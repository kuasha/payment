__author__ = 'maruf'


import payment
from payment.amazon.simplepay import *

from tornado import gen
from cosmos.service.requesthandler import RequestHandler

ACCESS_KEY  = ""
SECRET_KEY = ""
REQUEST_URL = "https://authorize.payments-sandbox.amazon.com/pba/paypipeline"
FPS_URL = "https://fps.sandbox.amazonaws.com/"

SIMPLE_PAY_SUCCESS_URL = "<your success url here>"
SIMPLE_PAY_FAILED_URL = "<your failed url here>"


#This should start the payment workflow
class AwsSimplePayHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        form_inputs = sp.create_form_inputs(100,                    # Amount
                                            "Test order",           # Description
                                            "123457",               # Reference Id
                                            None,                   # Immediate Return
                                            SIMPLE_PAY_SUCCESS_URL,
                                            SIMPLE_PAY_FAILED_URL,
                                            None,                   # Process Immediate
                                            None,                   # IPN Url
                                            1                       # Collect shipping address
                                            )

        output_form = sp.generate_form(form_inputs, REQUEST_URL)
        self.write(output_form)


#Map this top your SIMPLE_PAY_SUCCESS_URL
class AwsSimplePaySuccessHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        data = {k:''.join(v) for k,v in self.request.arguments.iteritems()}
        encoded_data = urllib.urlencode(data)
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        result = sp.verify_success_return(encoded_data, SIMPLE_PAY_SUCCESS_URL)
        self.write(result)
