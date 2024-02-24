#majority of the code was inspired by the yelp API documentation and sample code. with modifications to fit the needs of the project

from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib

from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode


API_KEY= 'YOUR_API_KEY'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com/v3'
SEARCH_PATH = '/businesses/search'
BUSINESS_PATH = '/businesses/'  # Business ID will come after slash.

DEFAULT_LOCATION = 'Manhattan, NY'
SEARCH_LIMIT = 50


def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': "Bearer " + api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location, offset):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'categories': 'restaurants',
        'limit': SEARCH_LIMIT,
        'offset': offset,
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def query_api(term, location):
    business_list = []

    for offset in range(0, 50, 50):
        response = search(API_KEY, term, location, offset)
        businesses = response.get('businesses')
        if not businesses:
            print(u'No businesses for {0} in {1} found.'.format(term, location))
            return
        business_list.extend(businesses)

    return business_list


def main():
    cusinesses = ['Indian', 'Mexican', 'Chinese']
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
