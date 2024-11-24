import json
import boto3

# S3 Client Initialization
s3_client = boto3.client('s3')

# Order Processing Bucket Name
bucket_name = "aws-exportedge-dev-order-processing-bucket"


# Upload Order Json in Order Processing Bucket
def s3_file_uplaod(order_json, order_json_str):
    
    order_id = order_json['order_id']
    key = "orders_json/" + order_id + "/" + order_id + ".json"
    
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=order_json_str,
        ContentType='application/json'
    )
    
    print(f"{order_id}.json file Uploaded to Bucket {bucket_name} under folder orders_json")


def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    order_json_str = event['Records'][0]['body']
    order_json = json.loads(order_json_str)
    
    print("order_json")
    print(order_json)
    
    s3_file_uplaod(order_json, order_json_str)
    
