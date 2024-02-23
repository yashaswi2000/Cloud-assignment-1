import {SQSClient, ReceiveMessageCommand, DeleteMessageCommand} from '@aws-sdk/client-sqs';
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand } from "@aws-sdk/lib-dynamodb";
import { SESClient, SendEmailCommand } from "@aws-sdk/client-ses"; 
import { defaultProvider } from '@aws-sdk/credential-provider-node'; // V3 SDK.
import { Client } from '@opensearch-project/opensearch';
import { AwsSigv4Signer } from '@opensearch-project/opensearch/aws';


const string_formatter = async (restaurants) => {
  let index = 1;
  let ans = ""
  for(const rest of restaurants) {
    ans = ans + index + ") " + "Restaurant Name: " + rest.Name + "\n" + "Address: " + rest.Address.display_address.join() + "\n" + "Rating: " + rest.Rating + "\n" + "Number of Reviews: " + rest["Number of Reviews"] + "\n\n";
    index = index + 1;
  }
  return ans;
}

const welcome_formatter = async (content) => {
  let restString = await string_formatter(content.restaurants);
  let ans = "Hey there, hope you are having a great day, please find below my recommendations for " + content['Cuisine'] + " restaurants for " + content['NumOfPeople'] + " people dining on " + content['DiningDate'] + " at " + content['DiningTime'] + "\n";
  ans = ans + "\n\n";
  ans = ans + restString;
  return ans;
}

const client = new Client({
  ...AwsSigv4Signer({
    region: 'us-east-1',
    service: 'es',  
    getCredentials: () => {
      const credentialsProvider = defaultProvider();
      return credentialsProvider();
    },
  }),
  node: 'https://search-elasticstarsearch-3lcridy75e33yvzpzhfh2r4n5i.us-east-1.es.amazonaws.com',
});

const get_messages = async () => {
  const client = new SQSClient({'region': "us-east-1"});
  const input = { // ReceiveMessageRequest
  QueueUrl: "https://sqs.us-east-1.amazonaws.com/471112677060/Q1", // required
  //ReceiveRequestAttemptId: "STRING_VALUE",
};
  const command = new ReceiveMessageCommand(input);
  const response = await client.send(command);
  console.log(response);
  
  const input_del = { // DeleteMessageRequest
  QueueUrl: "https://sqs.us-east-1.amazonaws.com/471112677060/Q1", // required
  ReceiptHandle: response.Messages[0].ReceiptHandle, // required
  };
  const command_del = new DeleteMessageCommand(input_del);
  const delresponse = await client.send(command_del);
  
  return JSON.parse(response.Messages[0].Body)
}


const get_openSearch = async (cuisine) => {
  const  url = "https://search-elasticstarsearch-3lcridy75e33yvzpzhfh2r4n5i.us-east-1.es.amazonaws.com"+"/restaurants/"+"_search"
  var query = {
  "size": 5, 
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": cuisine,
          "fields": ["Restaurant.Cuisine"]
        }
      },
      "random_score": {}
    }
    }
}
 var response = await client.search({
  index: "restaurants",
  body: query,
});

//console.log(response.body.hits.hits);//._source.Restaurant);
return response.body.hits.hits;

}

const get_dynamo = async (id) => {
  const client = DynamoDBDocumentClient.from(new DynamoDBClient({'region': "us-east-1"}));
const input = {
  TableName: "yelp-restaurants",
  IndexName: "Business_ID-index", 
  KeyConditionExpression: "Business_ID = :v1",
  ExpressionAttributeValues: {
    ":v1": id
  }
};
  const command = new QueryCommand(input);
  const response = await client.send(command);
  return response.Items[0]
  //console.log(response);
}

const send_email = async (content) => {
  const client = new SESClient({'region': 'us-east-1'});
const input = { // SendEmailRequest
  Source: "swavida@gmail.com", // required
  Destination: { // Destination
    ToAddresses: [ // AddressList
      content.Email,
    ],
  },
  Message: { // Message
    Subject: { // Content
      Data: "Your Handpicked Restaurants are ", // required
      Charset: "UTF-8",
    },
    Body: { // Body
      Text: {
        Data: await welcome_formatter(content), // required
        Charset: "UTF-8",
      },
    },
  },
};
const command = new SendEmailCommand(input);
const response = await client.send(command);
console.log(response);
}

export const handler = async (event) => {
  
  const res = await get_messages();
  const resOpenSearch = await get_openSearch(res.Cuisine);
  res.restaurants = [];
  for(const rest of resOpenSearch) {
    const full_rest = await get_dynamo(rest._id);
    res.restaurants.push(full_rest)
  }
  await send_email(res);
  
  // TODO implement
  const response = {
    statusCode: 200,
    body: JSON.stringify('Hello from Lambda!'),
  };
  return response;
};
