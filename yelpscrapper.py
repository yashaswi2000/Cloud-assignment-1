# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.

This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to https://docs.developer.yelp.com/docs/get-started for the API
documentation.

This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= '3Ci7a72bPec0X9O6ndPcWE8gOKR1hYxg-N3uEJgRlO7zGCJXIi6BGgvjS5XmdO4A0kDvwZr6IStrNG1_FarhNHi4aPBP9tTzBBkfdPi0-DuGcbHlrPgsiZUl6E3OZXYx'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com/v3'
SEARCH_PATH = '/businesses/search'
BUSINESS_PATH = '/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'chinese'
DEFAULT_LOCATION = 'New York City, NY'
SEARCH_LIMIT = 50


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': "Bearer " + api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location, offset):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'categories': 'restaurants',
        'limit': SEARCH_LIMIT,
        'offset': offset,
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """

    business_list = []

    for offset in range(0, 1000, 50):
        response = search(API_KEY, term, location, offset)
        businesses = response.get('businesses')
        if not businesses:
            print(u'No businesses for {0} in {1} found.'.format(term, location))
            return
        business_list.extend(businesses)

    return business_list


def main():
    cusinesses = ['Indian', 'Mexican', 'Chinese', 'Korean', 'Japanese']
    for cusinie in cusinesses:
        try:
            rests = query_api(cusinie, DEFAULT_LOCATION)
            file = open(cusinie + '.json', 'w')
            file.write(json.dumps(rests))
            file.close()
        except HTTPError as error:
            sys.exit(
                'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                    error.code,
                    error.url,
                    error.read(),
                )
            )


if __name__ == '__main__':
    main()
