# test_client.py

import unittest

from client import Connection
from mock import patch


def fake_get_data(test_self, test_api_name, test_url, test_success):
    if test_success == 'success':
        test_response = {'code':200,'response':{'metrics':[{'value': 'US', 'clicks': 1, 'link_count': 1}]}}
    else:
        test_response = {'code':404,'response':{"message":"FORBIDDEN"}}
    return test_response



class ClientTest(unittest.TestCase):
    # setup 
    def setUp(self):
        self.patcher = patch('client.Connection.get_data', fake_get_data)
        self.patcher.start()
        self.client = Connection('test_token')

    # teardown
    def tearDown(self):
        self.patcher.stop()

    # tests

    # successful response test
    def test_request_success(self):
        api_name = 'test_api_name'
        url = 'test_url'
        response = self.client.get_data(api_name, url, 'success')
        self.assertIn('code', response)
        self.assertEqual(response['code'], 200)
        print('client.py request success test')

    # Unsuccessful response test
    def test_request_fail(self):
        api_name = 'test_api_name'
        url = 'test_url'
        response = self.client.get_data(api_name, url,'failure')
        self.assertIn('code', response)
        self.assertEqual(response['code'], 404)
        print('client.py request failure test')

if __name__ == '__main__':
    unittest.main()