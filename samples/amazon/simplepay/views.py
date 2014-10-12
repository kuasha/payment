__author__ = 'maruf'

import payment
from payment.amazon.simplepay import *

from tornado import gen
from cosmos.service.requesthandler import RequestHandler
from cosmos.rbac.object import *
from cosmos.service.utils import MongoObjectJSONEncoder

DEBUG = True

ACCESS_KEY = "<your account access key here>"
SECRET_KEY = "<your account secret key here>"

REQUEST_URL = "https://authorize.payments-sandbox.amazon.com/pba/paypipeline"
FPS_URL = "https://fps.sandbox.amazonaws.com/"

ORDER_OBJECT_NAME = 'monohori.orders'
TOTAL_PRICE_FIELD = 'total_price'

ORDER_COMPLETE_URL = "https://monohori.com/#/a/<yourapp>/page/<complete page id>/"
ORDER_FAILEDE_URL = "https://monohori.com/#/a/<yourapp>/page/<failed page id>/"

SIMPLE_PAY_SUCCESS_URL = "<your success url here>"
SIMPLE_PAY_FAILED_URL = "<your failed url here>"

#Map this to your start payment page
class AwsSimplePayHandler(RequestHandler):
    @gen.coroutine
    def get(self, order_id):

        if order_id == "0000":
            order_id = self.get_cookie("orderId")

        print("Starting AWS payment for orderId: "+order_id)

        obj_serv = self.settings['object_service']
        columns = [TOTAL_PRICE_FIELD]
        cursor = obj_serv.load(SYSTEM_USER, ORDER_OBJECT_NAME, order_id, columns)
        order  = yield cursor
        if not order:
            raise tornado.web.HTTPError(404, "Not found")


        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        form_inputs = sp.create_form_inputs(order[TOTAL_PRICE_FIELD],                    # Amount
                                            "Test order",           # Description
                                            order['_id'],               # Reference Id
                                            1,                      # Immediate Return
                                            SIMPLE_PAY_SUCCESS_URL,
                                            SIMPLE_PAY_FAILED_URL,
                                            None,                   # Process Immediate
                                            None,                   # IPN Url
                                            1                       # Collect shipping address
                                            )

        output_form = sp.generate_form(form_inputs, REQUEST_URL)
        self.write(output_form)


#Map this to your success payment page
class AwsSimplePaySuccessHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        data = {k: ''.join(v) for k, v in self.request.arguments.iteritems()}
        order_id = data['referenceId']
        obj_serv = self.settings['object_service']
        columns = [TOTAL_PRICE_FIELD]
        cursor = obj_serv.load(SYSTEM_USER, ORDER_OBJECT_NAME, order_id, columns)
        order  = yield cursor
        if not order:
            raise tornado.web.HTTPError(404, "Not found")

        encoded_data = urllib.urlencode(data)
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        result = sp.verify_success_return(encoded_data, SIMPLE_PAY_SUCCESS_URL)

        if result == 'Success':
            save_data = {"owner":SYSTEM_USER, "payment": {"type": "AWS_SIMPLE_PAY", "data": data, "status": result}}

            promise = obj_serv.update(SYSTEM_USER, ORDER_OBJECT_NAME, order_id, save_data)
            result = yield promise
            data = MongoObjectJSONEncoder().encode({"error": result.get("err"),  "n":result.get("n"), "ok": result.get("ok"), "updatedExisting": result.get("updatedExisting")})
            self.redirect(ORDER_COMPLETE_URL)
        else:
            self.redirect(ORDER_FAILEDE_URL)
