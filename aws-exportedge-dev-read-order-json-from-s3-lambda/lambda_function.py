import json
import boto3

# S3 Client Initialization
s3_client = boto3.client('s3')


# Read Order Json from S3 Bucket
def read_order_json(bucket_name, object_key):
    
    obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    order_json_str = obj['Body'].read().decode('utf-8')
    order_json = json.loads(order_json_str)
    
    print("order json")
    print(order_json)
    
    return order_json

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    bucket_name = event['detail']['bucket']['name']
    object_key = event['detail']['object']['key']
    
    print(f"Bucket is '{bucket_name}' and Object Key is '{object_key}'")
    
    order_json = read_order_json(bucket_name, object_key)
    
    return order_json
