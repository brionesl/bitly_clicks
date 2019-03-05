# process_data.py

'''
Bitly Country Clicks API V1 
Author: Luis Briones

This program fetches data from 3 different Bitly API endpoints and calculates 
the average clicks per country for all the links in the user's default group over 
the past 30 days. [Clicks for each country / Number of links for that country]

The main function returns a dictioary object with response data. 
The object has 3 elements:
- api: Name of the API endpoint returning the object (used for testing and troubleshooting) 
- code: Code returned by the Endpoint (used for testing and troubleshooting)
- response: Country click data in json format if all calls to the Bitly APIs are successful
            or an error message returned by calls to individual Bitly endpoints

Successful Reponse:
{
    "country_metrics": [
        {
            "avg_clicks": int,
            "country": string,
            "total_clicks": int,
            "total_links": int
        }
    ],
    "default_group_id": string
}

Parameters:
main() function takes the following parameters:
token: Required
country_id: Optional (limits function return to one or more countries)

This code can be run as a standalone program but its main usage is to fetch and return data for
flask application server.py which will expose the data over HTTP
'''

# api class package
from client import Connection

# standard libraries
import json, itertools, time

# Bitly API endpoints
user_url = 'https://api-ssl.bitly.com/v4/user'
group_url = 'https://api-ssl.bitly.com/v4/groups/{}/bitlinks'
country_url = 'https://api-ssl.bitly.com/v4/bitlinks/{}/countries'


def main(token, country_id=None):
    # instantiate Connection class
    api_connection = Connection(token)
    user = api_connection.get_data('user', user_url)

    # check if there is an issue with user call and return response
    if user['code'] != 200: return user

    # get default user group from user api call and generate group url    
    user_default_group = user['response']['default_group_guid']
    group = api_connection.get_data('group', group_url.format(user_default_group))

    # get default user group from user api call and generate group url    
    user_default_group = user['response']['default_group_guid']

    # user proper pagination parameters to get all the links for the default group
    pagination_parm = {'page': '1'}
    link_pages = []
    while True:
        group_data = api_connection.get_data('group', group_url.format(user_default_group), params=pagination_parm)
        if group_data['code'] != 200: return group_data
        
        current_page = int(group_data['response']['pagination']['page'])
        link_pages.append(group_data['response']['links'])
        if not group_data['response']['pagination']['next']:
            break
        else:            
            current_page += 1
            pagination_parm = {'page': str(current_page)}

    # each page result is stored in in a list - "link_pages". code below unpacks and stores individual link ids to new list
    default_group_links = [link['id'] for page in link_pages for link in page]
    
    # list object stores clicks for each link and country
    country_clicks = []
    
    # as per requirements, only clicks for the last 30 days should be considered
    timeframe = {'unit': 'day', 'units': '30'}

    # each iteration of loop returns clicks for every country
    for link in default_group_links:
        # generate url for each link
        country_metrics = api_connection.get_data('country', country_url.format(link), params=timeframe)

        # check if there is an error with group call and return response
        if country_metrics['code'] != 200: return country_metrics 

        # append values for all countries to country_cicks list 
        for country in country_metrics['response']['metrics']:                
            country_clicks.append(
                {
                    'country': country['value'],
                    'clicks': int(country['clicks']),
                    'link_count': 1
                }
            )

    # setup return object structure
    country_data = {'default_group_id': user_default_group, 'country_metrics': []}
    
    #sort country_clicks list for faster performance
    country_clicks.sort(key=lambda x:x['country'])

    # filter results if country id(s) provided as parameter
    if country_id:
            # split and conver to set for faster performance
            country_id_set = set(country_id.split(','))
            country_clicks = [item for item in country_clicks if item['country'] in country_id_set] 
    
    # use itertools library to aggregate click statistics for each country
    for key, group in itertools.groupby(country_clicks, key=lambda x:x['country']):
        # itertools.groupby returns generator object 'group' which can only be accessed once. 
        # converting it to list to sum up multiple fields
        group = list(group)

        total_clicks = sum(d['clicks'] for d in group)
        total_links = sum(d['link_count'] for d in group)
        avg_clicks = total_clicks / total_links

        country_data['country_metrics'].append({
            'country': key,
            'total_clicks': total_clicks,
            'total_links': total_links,
            'avg_clicks': avg_clicks
        })
    
    return {'api':'country_clicks', 'code':200, 'response':country_data}
    

if __name__== "__main__":
    # standalone code execution of process_data.py for testing
    print(main('XxxxXXXXXxxxXXXXxxx'))



