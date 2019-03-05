# Bitly Country Clicks API V1

Author: Luis Briones

## Background
This application fetches data from 3 different Bitly API endpoints to calculate
the average clicks per country for all the links in the user's default group over
the past 30 days.

Total clicks for each country / Number of links for that country

The results are then exposed through a Python Flask API endpoint formatted as json.

API endpoints:
- / - home route which greeets user and provides instructions
- /api/v1/resources/country_clicks - main endpoint of this API; returns response data


## Installation
Please ensure python 3 and pip3 are properly installed in your system. Endpoint was written in Python 3.7 but will work with lower versions of python 3. 

python3 or python commands should both work as long as the versions are 3 and higher.
```bash
$ python3 -V
Python 3.7.0

$ pip3 -V
pip 18.0 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)
```
To run application, the following dependencies are required:

```
Flask, requests, mock
```

To install dependencies, use the included requirements.txt file. Some may already be installed:
```bash
pip3 install -r requirements.txt
```

If you receive any installation errors specific to your environment, please fix before proceeding

## Usage
Tor run api server, open the terminal (Mac) or command prompt (Windows) and navigate to the path where all the project files are located. Make sure the files below are available

```bash
$ ls -l
-rw-r--r--   1 user  staff     1908 Feb 20 16:44 client.py
-rw-r--r--   1 user  staff     5257 Feb 20 16:45 process_data.py
-rw-r--r--   1 user  staff       20 Feb 20 17:28 requirements.txt
-rw-r--r--   1 user  staff     2266 Feb 20 15:33 server.py
-rw-r--r--   1 user  staff     1418 Feb 20 17:08 test_client.py
-rw-r--r--   1 user  staff     1114 Feb 20 17:08 test_server.py
```

In the terminal window, execute the server.py program:
```bash
$ python3 server.py
```
You will see the output of the Flask server starting:
```bash
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 999-999-999
```

The default address is http://127.0.0.1:5000/

If you navigate to this address on your browser, you'll be greeted with instructions on usage

#### API Queries
To query the endpoint, you can use your favorite API client (Postman) or use curl commands on the terminal window.

You must submit a Bitly access token with your request in the form of a Bearer token. Below are the 3 types of queries to the /country_clicks endpoint:

Query all countries:
```bash
curl -X GET http://localhost:5000/api/v1/resources/country_clicks -H "Authorization: Bearer YOURACCESSTOKEN"
```
Query 1 country:
```bash
curl -X GET http://localhost:5000/api/v1/resources/country_clicks?country_id=US -H "Authorization: Bearer YOURACCESSTOKEN"
```

Query multiple countries
```bash
curl -X GET http://localhost:5000/api/v1/resources/country_clicks?country_id=US,FR,CA -H "Authorization: Bearer YOURACCESSTOKEN"
```
#### Sample response
```json
{
    "custom_metrics": [
        {
            "avg_clicks": 2,
            "country": "EC",
            "total_clicks": 2,
            "total_links": 1
        },
        {
            "avg_clicks": 2.3333333333333335,
            "country": "US",
            "total_clicks": 7,
            "total_links": 3
        }
    ],
    "default_group_id": "XXXXZZZZZYYYY"
}
```

## Design
Every module has been thoroughly documented to explain the logic behind the code. This will serve as a higher level description of the decisions made when implementing the solution

#### server.py

Once Flask server starts, it listens for HTTP requests on the 2 routes setup by the program.

The '/' route, simply provides a welcome message to the user.

The '/country_clicks' route accesses the get_country_clicks function and first checks for the proper authorization in the request header and returns an error response if it is missing. This function also parses any parameters passed in the request (country_id)

Once this is handled, the function calls the main() function of the process_data file to continue.

#### process_data.py
This is the main driver for fetching, formatting and returning the proper metrics from the Bitly API.

To call the Bitly API, a Connection class in the client.py file is imported. This creates a connection object that can be reused for each call to the different Bitly API endpoints (more on the class in the next section)

The requirement was to calculate the average clicks per country for all the links in the user's default group over the past 30 days. To accomplish this 3 things need to be done:
1. Get the user's default group from 'https://api-ssl.bitly.com/v4/user'
2. Get all the bitlinks for that group from 'https://api-ssl.bitly.com/v4/groups/{default_group}/bitlinks'
3. Fetch country metrics (clicks) for each of the links returned in Step 2 from 'https://api-ssl.bitly.com/v4/bitlinks/{}/countries'

The program performs these 3 steps in the following manner:
- instantiate Connection class with access token as a parameter (obtained from flask server request)
- call get_data method with the /user endpoint parameter and obtain default_group_guid
- call get_data method with the default_group_guid parameter to obtain all bitlinks associated with group
- Loop through all links from previous step and call the get_data method with the url for each bitlink, as well as unit parameters to limit the response to the last 30 days.
- If country_id is passed to the main() function, the items are parsed and only returned items with those ids are stored in a list (country_clicks) which will later be aggregated. If not, all the items are stored in country_clicks
- The Bitly API endpoints don't allow specific country parameters to be passed. To add the this functionality to the new endpoint, we allow a country_id parameter to be passed in the API query
- After looping through the links, the python itertools library is used to aggregate the links by country
- Finally the response is sent back to the calling function - get_country_clicks in the server.py file

#### client.py
This file contains the Connection class which has only one method - get_data but additional methods can easily be added to perform other functions (POST, PATCH, etc.)

The class accepts a token variable as a parameter because all the API endpoints use the same access token. This provides reusability

The get_data method returns a dictionary with the api name, a response status code and the response

For errors, exception handling was designed to return the error description in the same way a successful reponse does (a dictionary) This provides the user with a description of the issue.

#### Some notes
- Different methods were timed to ensure optimal performance. For example, aggregating the clicks through each iteration of the loop was slower than adding all the items to a list and aggregating later.
- Pandas library was also tested for aggregation but it was significantly slower than itertools library

## Testing
Unit testing was performed using the standard unittest python library:
- test_server.py - tests the server routes to ensure the user hitting the api works as expected
- test_client.py - tests the Connection class by faking the functionality of the get_data method and feeding test responses to the application.

Additional testing would need to be done before moving application to production but for purposes of this exercise, I wanted to show how the proper testing could be done.

To test application, the individual files can be executed or a testing tool can be used (nose, nose2, etc.) but it's not required

```bash
$ python3 test_client.py
>>>
client.py request failure test
.client.py request success test
.
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```
To test the server, launch test with command below and stop the server once it has started(ctrl+c) This will allow you to see results
```bash
$ python3 test_server.py
>>>
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 999-999-999
^Ccountry_clicks route test
.home route test
.invalid route test
.
----------------------------------------------------------------------
Ran 3 tests in 0.009s

OK
```
