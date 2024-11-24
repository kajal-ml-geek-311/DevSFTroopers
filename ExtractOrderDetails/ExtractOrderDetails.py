import boto3
import json

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket name and object key from the Step Function input
    bucket_name = event['s3_bucket']
    object_key = event['s3_key']
    
    # Read the file content from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    order_details = json.loads(response['Body'].read())
    
    # Return the extracted order details
    return order_details
