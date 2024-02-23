import boto3
import json

# --- Helpers that build all of the responses ---
def close_intent_with_fulfillment(event):
    return {
        "sessionState": {
            "intent": {
                "name": event['sessionState']['intent']['name'],
                "state": "Fulfilled"
            },
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled"
            }
        },
        "messages": [{
            "contentType": "PlainText",
            "content": "Thank you! You will receive the recommendations soon."
        }]
    }

def send_to_sqs(data):
    sqs = boto3.client('sqs')
    
    queue_url = 'https://sqs.us-east-1.amazonaws.com/471112677060/Q1'
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(data)
    )
    return response

def elicit_slot(event, slot_to_elicit, message=None):
    slot_messages = {
        'Location': "Where are you located? (Only Manhattan is supported currently)",
        'Cuisine': "Please choose a cuisine: Indian, Mexican, Chinese",
        'DiningDate': "On which  would you like to book a table for?",
        'DiningTime': "At what time would you like to book a table for?",
        'NumOfPeople': "How many are in your party?",
        'Email': "Please provide your email address."
    }

    message_to_use = message if message else slot_messages.get(slot_to_elicit, f"Can you provide the {slot_to_elicit}?")

    return {
        "sessionState": {
            "intent": {
                "name": event['sessionState']['intent']['name'],
                "slots": event['sessionState']['intent']['slots'],
                "state": "InProgress"
            },
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit
            }
        },
        "messages": [{
            "contentType": "PlainText",
            "content": message_to_use
        }]
    }
    
def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def safe_int(n):
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    try:
        return func()
    except KeyError:
        return None

