# test_bitly_api_py

import unittest
 
from server import app
 
class BasicTests(unittest.TestCase):
    #setup
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
    
    # teardown
    def tearDown(self):
        pass
 

    # tests

    #test home directory route
    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print('home route test')
    
    # test country_clicks route
    def test_get_country_clicks(self):
        response = self.app.get('/api/v1/resources/country_clicks', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print('country_clicks route test')

    # test invalid route
    def test_invalid_endpoint(self):
        response = self.app.get('/api/v1/resources/invalid', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        print('invalid route test')

if __name__ == "__main__":
    unittest.main()
