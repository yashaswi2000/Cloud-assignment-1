import boto3
import json


client = boto3.client('apigateway')
response = client.import_rest_api(
    failOnWarnings=True,
    parameters={
        "endpointConfigurationTypes" : "REGIONAL"
    },
    body= open('apisetup.yaml', 'r').read()
)
print(response)

res = client.create_deployment(
    restApiId=response['id'],
    stageName='dev',
    description='testing stage',
)

print(res)
