import json
import boto3

# S3 Client Initialization
s3_client = boto3.client('s3')

# Order Document S3 Bucket
bucket_name = "aws-exportedge-dev-order-processing-bucket"


# Get Order Document's Key List
def doc_key_list(prefix):
    
    doc_key_list = []
    
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )
    
    for obj in response['Contents']:
        doc_key_list.append(obj['Key'])
        
    print("doc key list")
    print(doc_key_list)
    
    return doc_key_list
    

# Get Order Document's PreSigned URL's 
def presigned_url_list(doc_key_list):
    
    presigned_url_list = []
    
    expires_in = 3600
    
    for doc_key in doc_key_list:
        
        presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket' : bucket_name,
                    'Key' : doc_key
                },
                ExpiresIn=expires_in
            )
            
        presigned_url_list.append(presigned_url)
    
    print("presigned url list")
    print(presigned_url_list)
    
    return presigned_url_list
    

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    order_id = event['path'].split("/")[2]
    prefix = f"orders_docs/{order_id}/"
    
    doc_keys_list = doc_key_list(prefix)
    presigned_urls_list = presigned_url_list(doc_keys_list)
    
    order_details = {
        "body": str(presigned_urls_list)
    }
    
    return order_details
