import json
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

AWS_ACCESS_KEY = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_KEY = 'AWS_SECRET_ACCESS_KEY'
region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = 'search-elasticstarsearch-3lcridy75e33yvzpzhfh2r4n5i.us-east-1.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com

es = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

print(es.info())



response = es.indices.create(index='restaurants',
                             body={
                                 'mappings': {
                                     'properties': {
                                     'Restaurant': {
                                        'properties': {
                                            'RestaurantID': {'type': 'text'},
                                            'Cuisine': {'type': 'text'},
                                        }
                                    }
                                 }
                             }})

for cusine in ['Indian', 'Chinese', 'Mexican']:
    file = open(cusine+'.json', 'r')
    data = json.loads(file.read())
    file.close()
    for i in range(len(data)):
        response = es.index(    
            index='restaurants',
            body={
                'Restaurant': {
                    'RestaurantID': data[i]['id'],
                    'Cuisine': cusine,
                }
            },
            id=data[i]['id'],
        )
        print(response)

    res = es.search(index='restaurants', body={'query': {'match_all': {}}})

    print(res)
