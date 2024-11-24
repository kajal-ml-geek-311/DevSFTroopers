import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# OpenSearch Configuration's
host = 'search-exportedge-opensearch-q2ooymtdrrvwltkjiriduawf5u.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
index_name = 'order-index'


# OpenSeacrh Index Document
def index_document(awsauth, order_document):
    
    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        http_compress = True,
        connection_class = RequestsHttpConnection
    )
    
    print("order_document")
    print(order_document)
    
    search.index(index=index_name, body=order_document, refresh=True)
    
    print(f"Order Record Indexed Sucessfully in OpenSearch {index_name} Index")
    

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    order_document = event["Records"][0]["dynamodb"].get("NewImage")
    
    index_document(awsauth, order_document)
    
    return f"Order Record Indexed Sucessfully in OpenSearch {index_name} Index"