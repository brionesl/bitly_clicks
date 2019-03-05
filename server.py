# server.py

'''
Bitly Country Clicks API V1 
Author: Luis Briones

This program starts a FLask server to expose the results of process_data.py module.
There are 2 routes:
- '/': home() function displays text welcoming user and providing some instructions
- '/api/v1/resources/country_clicks': get_country_clicks() function performs 2 functions:
    - Parses authorization header and parameters
    - Calls process_data module with token and parameters

Default Port: 5000

Authentication:
A Bearer token must be included in the request header

'''

# 3rd party libraries
import flask
from flask import jsonify, request

# project files
import process_data

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return jsonify({'title': 'Bitly Country Clicks API V1',\
    'message': 'To access this API endpoint you will need to query /api/v1/resources/country_clicks.\
 Please ensure that a Bearer token is provided with your query',\
    'sample_queries':\
    ['curl -X GET http://localhost:5000/api/v1/resources/country_clicks -H "Authorization: Bearer YOURACCESSTOKEN"',\
    'curl -X GET http://localhost:5000/api/v1/resources/country_clicks?country_id=US -H "Authorization: Bearer YOURACCESSTOKEN"',\
    'curl -X GET http://localhost:5000/api/v1/resources/country_clicks?country_id=US,FR,CA -H "Authorization: Bearer YOURACCESSTOKEN"']})

@app.route('/api/v1/resources/country_clicks', methods=['GET'])
def get_country_clicks():
    auth_header = request.headers.get('Authorization')
    # check if authorization header is included and parse token
    if auth_header:
        if 'Bearer' not in auth_header:
            return jsonify({'status': 'fail', 'message': 'Token must be Bearer Token'})

        try:
            access_token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'status': 'fail', 'message': 'Token malformed'})
    else:
        return jsonify({'status': 'fail', 'message': 'Token empty. Please provide a valid bearer token'})

    country_id = None
    if 'country_id' in request.args:
        country_id = request.args['country_id']

    country_clicks = process_data.main(access_token,country_id=country_id)['response']
    return jsonify(country_clicks)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Resource Not Found.</p>", 404

app.run()