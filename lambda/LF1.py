import json
import datetime
import boto3
from utils import *

def lambda_handler(event, context):
    intent_name = event['sessionState']['intent']['name']

    if intent_name == "GreetingIntent":
        return greeting_intent(intent_name)
    elif intent_name == "ThankYouIntent":
        return thank_you_intent(intent_name)
    elif intent_name == "DiningSuggestionsIntent":
        return dining_suggestion_intent(event)
    
def greeting_intent(intent_name):
    message = "Hi there, how can I help?"
    return {
      "sessionState": {
        "dialogAction": {
          "type": "Close"
        },
        "intent": {
          "name": intent_name,
          "state": "Fulfilled"
        }
      },
      "messages": [{
        "contentType": "PlainText",
        "content": message
      }]
    }
    
def thank_you_intent(intent_name):
    message = "You're welcome!"
    return {
      "sessionState": {
        "dialogAction": {
          "type": "Close"
        },
        "intent": {
          "name": intent_name,
          "state": "Fulfilled"
        }
      },
      "messages": [{
        "contentType": "PlainText",
        "content": message
      }]
    }
    
def validate_dining_suggestion(location, cuisine, num_people, date, time):
    locations = ['manhattan']
    if location is not None and location .lower() not in locations:
        return build_validation_result(False,
                                       'location',
                                       'Only Manhattan is supported currently. Please choose Manhattan.')
                                       
    cuisines = ['chinese', 'mexican', 'indian']
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'cuisine',
                                       'Cuisine not available. Please try from the given list.')

    if num_people is not None:
        num_people = int(num_people)
        if num_people > 20 or num_people <= 0:
            return build_validation_result(False,
                                           'numofpeople',
                                           'Maximum 20 people allowed. Try again')
                                           
    if date is not None:
        if not is_valid_date(date):
            return build_validation_result(False, 'date',
                                           'I did not understand that. Please provide a valid date.')

    if time is not None:
        if len(time) != 5:
            return build_validation_result(False, 'time', 'Please provide time in HH:MM format.')

        hour, minute = map(int, time.split(':'))
        if hour < 11 or hour > 23:
            return build_validation_result(False, 'time',
                                           'Our business hours are from 11 a.m. to 11 p.m. Can you specify a time during this range?')

    return build_validation_result(True, None, None)

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {'isValid': is_valid, 'violatedSlot': violated_slot}

    return {'isValid': is_valid, 'violatedSlot': violated_slot, 'message': {'content': message_content, 'contentType': 'PlainText'}}

def is_valid_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_slot_value(slots, slot_name):
        slot = slots.get(slot_name, {})
        if slot and 'value' in slot and 'interpretedValue' in slot['value']:
            return slot['value']['interpretedValue']
        return None

def check_dynamo_db(email):
   
    dynamodb = boto3.resource('dynamodb')
    table_name = 'user-preferences'
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'Email': email})
    print(response)
    return response.get('Item')
    
def send_email_via_ses(email_data):
    ses = boto3.client('ses', region_name='us-east-1')
    
    try:
        response = ses.send_email(
            Source=email_data['Source'],
            Destination={
                'ToAddresses': email_data['Destination']['ToAddresses'],
            },
            Message={
                'Subject': {
                    'Data': email_data['Message']['Subject']['Data'],
                    'Charset': email_data['Message']['Subject']['Charset']
                },
                'Body': {
                    'Text': {
                        'Data': email_data['Message']['Body']['Text']['Data'],
                        'Charset': email_data['Message']['Body']['Text']['Charset']
                    },
                }
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
        return response
    except Exception as e:
        print("Error sending email", e)
        return None

def dining_suggestion_intent(event):
    slots = event['sessionState']['intent']['slots']
    
    email_slot_value = get_slot_value(slots, 'Email')
    
    if not email_slot_value:
        return elicit_slot(event, 'Email')
        
    user_record = check_dynamo_db(email_slot_value)
    
    samepref_slot_value = get_slot_value(slots, 'SamePreference')
    
    if not user_record:
        samepref_slot_value = 'no'
    
    else:
        print(samepref_slot_value)
        if not samepref_slot_value:
            print("inside same preferences\n")
            rest = elicit_slot(event, 'SamePreference')
            print(rest)
            return rest
            
        if samepref_slot_value.lower() == 'yes':
            # Send email
            body = json.loads(user_record['Body'])
            send_email_via_ses(body)
            return close_intent_with_fulfillment(event)
        
    slot_order = ['Location', 'Cuisine', 'NumOfPeople', 'DiningDate', 'DiningTime', 'Email']
        
    for slot_name in slot_order:
        # Get the value of the current slot
        slot_value = get_slot_value(slots, slot_name)
        
        # If the slot is not filled, elicit this slot
        if not slot_value:
            return elicit_slot(event, slot_name)
        
        # If the slot is filled, validate the slot
        if slot_name == 'Location':
            validation_result = validate_dining_suggestion(slot_value, None, None, None, None)
        elif slot_name == 'Cuisine':
            validation_result = validate_dining_suggestion(None, slot_value, None, None, None)
            #message = 'Please choose a cuisine: Italian, Indian, Mexican, Chinese'
        elif slot_name == 'NumOfPeople':
            validation_result = validate_dining_suggestion(None, None, slot_value, None, None)
            #message = 'When would you like to book a table for?'
        elif slot_name == 'DiningDate':
            validation_result = validate_dining_suggestion(None, None, None, slot_value, None)
            #message = 'At what time would you like to book a table for?'
        elif slot_name == 'DiningTime':
            #message = 'How many are in your party?'
            validation_result = validate_dining_suggestion(None, None, None, None, slot_value)
        elif slot_name == 'Email':
            validation_result = validate_dining_suggestion(None, None, None, None, None)
        
        # Check the validation result and elicit the slot again if validation fails
        if not validation_result['isValid']:
            return elicit_slot(event, slot_name, validation_result['message']['content'])
            
    details = {
        'Location': get_slot_value(slots, 'Location'),
        'Cuisine': get_slot_value(slots, 'Cuisine'),
        'NumOfPeople': get_slot_value(slots, 'NumOfPeople'),
        'DiningDate': get_slot_value(slots, 'DiningDate'),
        'DiningTime': get_slot_value(slots, 'DiningTime'),
        'Email': get_slot_value(slots, 'Email')
    }
    
    # Send data to SQS
    send_to_sqs(details)
        

    # If all slots are valid, proceed with fulfillment
    return close_intent_with_fulfillment(event)