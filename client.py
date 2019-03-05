# client.py

'''
Bitly Country Clicks API V1 
Author: Luis Briones

This file stores classes used to connect to Bitly API endpoints.

Parameters:
api_name: used to identify endpoint
url: api endpoint uri
axs_token: access token
params: optional parameter variable

Methods:
get_data()

Usage:
#instantiate 
api_object = Connection('apiName', 'http://sample.com/endpoint', 'XXXXXXXXXXXX')
# call method
response_data = api_object.get_data()

Future enhancements:
Additional methods can be added to POST, PATCH, UPDATE different endpoints
'''

# 3rd party libraries
import requests

# standard libraries
import logging, http.cookiejar, json
from requests_futures.sessions import FuturesSession

logger = logging.getLogger('avg_country_clicks')

class Connection:
    # initalizing token variable in  class constructor so that all methods have access
    def __init__(self, axs_token):
        self.axs_token = axs_token
        self.header = {
            'Authorization': 'Bearer {}'.format(self.axs_token)
        }
        # using FutureSession for multiprocessing requests
        self.link_session = FuturesSession(max_workers=10)

    def get_data(self, api_name, url, params=None):
        try:
            response = self.link_session.request("GET", url, headers=self.header, params=params)
            json_content= json.loads(response.result().content.decode("utf-8"))
            return {'api':api_name, 'code': response.result().status_code, 'response':json_content}

        # exceptions don't end execution, errors are returned to alert user of issue
        except (requests.ConnectionError, requests.Timeout) as e:
            return {'api':api_name, 'code':'Connection Error', 'response': str(e)}
        
        except requests.exceptions.HTTPError as e:
            return {'api':api_name, 'code': e.response.status_code, 'response': e.response.text.strip()}
            # error logging
            logger.exception('There was an problem with the Bitly API Service')