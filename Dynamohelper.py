import boto3
import json
import requests
from datetime import datetime
from decimal import Decimal


dyno = boto3.resource('dynamodb')

for cusine in ['Indian', 'Chinese', 'Mexican']:
    file = open(cusine+'.json', 'r')
    data = json.loads(file.read(), parse_float=Decimal)
    file.close()
    for i in range(len(data)):
        response = dyno.Table('yelp-restaurants').put_item(
            Item={
                "Business_ID" : data[i]['id'],
                "Name" : data[i]['name'],
                "Address" : data[i]['location'],
                "Coordinates": data[i]['coordinates'],
                "Number of Reviews": data[i]['review_count'],
                "Rating" : data[i]['rating'],
                "Zip Code": data[i]['location']['zip_code'],
                'Cuisine': cusine,
                'insertedAtTimestamp': str(datetime.now()),
            }
        )
        print(response)

response = dyno.Table('yelp-restaurants').query( 
    IndexName='Business_ID-index',
    KeyConditionExpression= 'Business_ID = :value',
    ExpressionAttributeValues= {
        ':value': 'xq0cX_DgxiJMXwhmEl9kUA'
    }
)
print(response)
