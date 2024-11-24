import json
import boto3

# DynamoDb Client Initialization
dynamodb_client = boto3.client("dynamodb")

# Dynamodb Table
dynamodb_table = "aws-exportedge-dev-order-dynamodb-table"


# Get Order List
def order_list():
    
    response = dynamodb_client.scan(TableName=dynamodb_table)
    
    order_list = []
    
    for item in response['Items']:
        order = {}
        order["order_id"] = item["order_id"]["S"]
        order["order_placed_timestamp"] = item["order_placed_timestamp"]["S"]
        order["order_status"] = item["order_status"]["S"]
        order_list.append(order)
        
    print("order list")
    print(order_list)
    
    response = {
        "body": str(order_list)
    }
    
    return response

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    response = order_list()
    
    return response
