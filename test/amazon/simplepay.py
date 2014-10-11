from mock import MagicMock

__author__ = 'maruf'
import unittest
import payment.amazon.simplepay

ACCESS_KEY = "ADIAJIJL5IWFAQATO2TQ"
SECRET_KEY = "8A+aOofm5w01gBHjWAYR56Sx9XFgReW12DzjrlDi"
REQUEST_URL = "https://authorize.payments-sandbox.amazon.com/pba/paypipeline"
FPS_URL = "https://fps.sandbox.amazonaws.com/"


class LoggedTestCase(unittest.TestCase):

    def test_generate_signature(self):
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        secret_key = "testsecrectkey123"
        verb = "POST"
        request_url = "https://authorize.payments-sandbox.amazon.com/pba/paypipeline"
        values = {"name": "test"}
        sign = sp.generate_signature(secret_key, verb, values, request_url)
        expected_sign = "0vl1XR6IdKxqdkX/Dn2SmrRBMNnlFfq/EVKQkap/J/k="
        self.failUnlessEqual(sign, expected_sign)
        
    def test_create_form_inputs(self):
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        form = sp.create_form_inputs(100, "Test order", "123456", None, "https://example.com/success/123456",
                                     "https://example.com/failed/123456", None, None, 1)

        expected_form = {'signatureVersion': '2', 'referenceId': '123456','returnUrl': 'https://example.com/success/123456',
                         'description': 'Test order', 'collectShippingAddress': '1', 'accessKey': ACCESS_KEY,
                         'amount': '100', 'signatureMethod': 'HmacSHA256','abandonUrl': 'https://example.com/failed/123456',
                         'signature': '9cL0vgSDoQbSJQRWY1cfN6S4YqpOuACn/ObRgFAoebo='
                        }

        self.failUnlessEqual(len(form.keys()), len(expected_form.keys()))
        for key in expected_form.keys():
            self.failUnlessEqual(form[key], expected_form[key])

    def test_verify_success_return(self):
        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)

        success_return = '<VerifySignatureResponse xmlns="http://fps.amazonaws.com/doc/2008-09-17/">' \
                         '  <VerifySignatureResult>' \
                         '    <VerificationStatus>Success</VerificationStatus>' \
                         '  </VerifySignatureResult>  <ResponseMetadata>' \
                         '    <RequestId>197e2085-1ed7-47a2-93d8-d76b452acc74:0</RequestId>' \
                         '  </ResponseMetadata>' \
                         '</VerifySignatureResponse>'

        failed_return = '<VerifySignatureResponse xmlns="http://fps.amazonaws.com/doc/2008-09-17/">' \
                         '  <VerifySignatureResult>' \
                         '    <VerificationStatus>VerifyFailed</VerificationStatus>' \
                         '  </VerifySignatureResult>  <ResponseMetadata>' \
                         '    <RequestId>197e2085-1ed7-47a2-93d8-d76b452acc74:0</RequestId>' \
                         '  </ResponseMetadata>' \
                         '</VerifySignatureResponse>'

        #Test success
        sp.execute_fps = MagicMock(name='execute_fps', return_value=success_return)
        data = {"test": "success"}
        success_url = "http://example.com/success/1234456"

        result = sp.verify_success_return(data, success_url)
        self.failUnlessEqual(result, "Success")
        sp.execute_fps.assert_called_once_with('VerifySignature', 'GET', HttpParameters=data, UrlEndPoint=success_url)

        #Test failure
        sp.execute_fps = MagicMock(name='execute_fps', return_value=failed_return)
        data = {"test": "failed"}
        faiuled_url = "http://example.com/success/123000"

        result = sp.verify_success_return(data, faiuled_url)
        self.failUnlessEqual(result, "VerifyFailed")
        sp.execute_fps.assert_called_once_with('VerifySignature', 'GET', HttpParameters=data, UrlEndPoint=faiuled_url)

    def test_generate_form(self):
        expected_form = '<form action="https://authorize.payments-sandbox.amazon.com/pba/paypipeline" method="POST">\n' \
                        '    <input type="image" src="https://authorize.payments.amazon.com/pba/images/payNowButton.png" border="0" />\n' \
                        '    <input type="hidden" name="signatureVersion" value="2" />\n' \
                        '    <input type="hidden" name="referenceId" value="123456" />\n' \
                        '    <input type="hidden" name="returnUrl" value="https://example.com/success/123456" />\n' \
                        '    <input type="hidden" name="description" value="Test order" />\n' \
                        '    <input type="hidden" name="collectShippingAddress" value="1" />\n' \
                        '    <input type="hidden" name="accessKey" value="ADIAJIJL5IWFAQATO2TQ" />\n' \
                        '    <input type="hidden" name="amount" value="100" />\n' \
                        '    <input type="hidden" name="signatureMethod" value="HmacSHA256" />\n' \
                        '    <input type="hidden" name="signature" value="9cL0vgSDoQbSJQRWY1cfN6S4YqpOuACn/ObRgFAoebo=" />\n' \
                        '    <input type="hidden" name="abandonUrl" value="https://example.com/failed/123456" />\n' \
                        '</form>\n'

        sp = payment.amazon.simplepay.SimplePay(ACCESS_KEY, SECRET_KEY, REQUEST_URL, FPS_URL)
        form_inputs = sp.create_form_inputs(100, "Test order", "123456", None, "https://example.com/success/123456",
                                     "https://example.com/failed/123456", None, None, 1)

        output_form = sp.generate_form(form_inputs, REQUEST_URL)
        self.failUnlessEqual(output_form, expected_form)

