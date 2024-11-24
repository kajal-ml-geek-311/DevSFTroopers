import json
import boto3

# S3 Client Initialization
s3_client = boto3.client('s3')

# SQS Client Initialization
sqs_client = boto3.client('sqs')

# SQS Queue URL
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/637423411939/aws-exportedge-dev-receive-order-metadata-json-sqs"


# Send SQS Queue Message
def send_sqs_message(order_json_str):
        
    response = sqs_client.send_message(
        QueueUrl = sqs_queue_url,
        MessageBody = order_json_str
    )
    
    print(f"order json  : {order_json_str}")
    

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    bucket_name = event['detail']['bucket']['name']
    key = event['detail']['object']['key']
    
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    
    order_json_str = obj['Body'].read().decode('utf-8')
    
    send_sqs_message(order_json_str)
   
    print("Order's JSON pushed to SQS Queue")
