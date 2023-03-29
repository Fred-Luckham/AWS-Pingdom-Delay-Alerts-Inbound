import os
import json
import boto3

client = boto3.client('ec2')

def lambda_handler(event, context):
    print(event)
    source_check(event, context)

def source_check(event, context):
    body = extract_body(event)
    subject = f"Site Outage: {body['check_params']['full_url']}"
    print(body)
    output_dict = {
        "check_name": body['check_name'],
        "check_type": body['check_type'],
        "state_changed_timestamp": body['state_changed_timestamp'],
        "state_changed_utc_time": body['state_changed_utc_time'],
        "long_description": body['long_description'],
        "current_state": body['current_state'],
        "full_url":body['check_params']['full_url'],
        "subject": subject
    }
    if os.environ['Pingdom'] in event['headers']['user-agent']:
        hand_to_step_function(output_dict)
    elif os.environ['SNS'] in event['headers']['user-agent']:
        pass
    else:
        print("No known source")

def hand_to_step_function(output_dict):
    print(output_dict)
    client = boto3.client('stepfunctions')
    response = client.start_execution(
        stateMachineArn= os.environ['StateMachineARN'],
        input= json.dumps(output_dict)
    )

def extract_body(event):
    body = json.loads((event["body"]))
    return body
