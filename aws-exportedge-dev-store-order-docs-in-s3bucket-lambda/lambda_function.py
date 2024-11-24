import json
import boto3

# S3 Client Initialization
s3_client = boto3.client('s3')

# Order Processing Bucket Name
order_processing_bucket_name = "aws-exportedge-dev-order-processing-bucket"


# Order Document Copied in Order Processing Bucket
def s3_file_copy(bucket_name, key):
    
    key_split = key.split("_")
    order_id = key_split[0]
    
    doc_key = "orders_docs/" + order_id + "/" + key
    
    response = s3_client.copy_object(
        CopySource={
            "Bucket" : bucket_name,
            "Key" : key
        },
        Bucket=order_processing_bucket_name,
        Key=doc_key
    )
    

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    bucket_name = event['detail']['bucket']['name']
    key = event['detail']['object']['key']
    
    print(f"Bucket is {bucket_name} and key is {key}")
    
    s3_file_copy(bucket_name, key)
    
    print("Order Document Copied in Order Processing S3 Bucket Succesfully")
