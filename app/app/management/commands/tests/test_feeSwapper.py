from unittest import mock

from django.core.management import call_command

from test_plus.test import TestCase


class MockResponse:
    def __init__(self, status_code, json_data=None):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = True

    def json(self):
        return self.json_data


class feeSwapperTest(TestCase):
    """Define tests for feeSwapper management command
    #@mock.patch('feeSwapper.requests.get', return self.resp)"""
    resp = MockResponse(200,json_data={"status":"1","result":[{"symbol":"OMG","name":"OMGToken","decimals":"18","contractAddress":"0x879884c3c46a24f56089f3bbbe4d5e38db5788c0","balance":"10000000"},{"symbol":"WEENUS","name":"Weenus 💪","decimals":"18","contractAddress":"0xaff4481d10270f50f203e0763e2597776068cbc5","balance":"1000000000000000000000"},{"symbol":"BAT","name":"Basic Attention Token","decimals":"18","contractAddress":"0xda5b056cfb861282b4b59d29c9b395bcc238d29b","balance":"0"},{"symbol":"MKR","name":"Maker","decimals":"18","contractAddress":"0xf9ba5210f91d0474bd1e1dcdaec4c58e359aad85","balance":"100000000000000000"}],"message":"OK"})
    
    @mock.patch('app.management.commands.feeSwapper.requests.get',return_value=resp)
    @mock.patch('app.management.commands.feeSwapper.Command.sell_token',return_value=True)
    def test_feeSwapper(self, response, sell_response):
        tokenList = call_command('feeSwapper')
        assert tokenList == "BAT"
