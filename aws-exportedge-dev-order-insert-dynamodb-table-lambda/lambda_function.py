import json
import boto3

# DynamoDb Client Initialization
dynamodb_client = boto3.client("dynamodb")

# Dynamodb Table
dynamodb_table = "aws-exportedge-dev-order-dynamodb-table"


# Order Item meta data Json
def order_item(event):
 
    item = {
        "order_id" : {"S" : event["order_id"]},
        "order_placed_timestamp" : {"S" : event["order_placed_timestamp"]},
        "product_name" : {"S" : event["product_name"]},
        "product_category" : {"S" : event["product_category"]},
        "product_price" : {"S" : event["product_price"]},
        "product_specifications" : {"S" : event["product_specifications"]},
        "product_dimensions" : {"S" : event["product_dimensions"]},
        "product_weight" : {"S" : event["product_weight"]},
        "product_quantity" : {"S" : event["product_quantity"]},
        "product_sku_id" : {"S" : event["product_sku_id"]},
        "customer_prime_member" : {"S" : event["customer_prime_member"]},
        "customer_mobile_number" : {"S" : event["customer_mobile_number"]},
        "customer_email_adress" : {"S" : event["customer_email_adress"]},
        "customer_delivery_address" : {"S" : event["customer_delivery_address"]},
        "warehouse_pickup_address" : {"S" : event["warehouse_pickup_address"]},
        "compliance_status" : {"S" : event["compliance_status"]},
        "order_status" : {"S" : "Open"}
    }
    
    return item


# Insert Order metadata Json in Order DynamoDb Table
def insert_order_dynamodbtable(item):
    
    response = dynamodb_client.put_item(
                TableName=dynamodb_table,
                Item=item
    )
    
    print("Order metadata Stored in Dynamodb Table")

def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    item = order_item(event)
    insert_order_dynamodbtable(item)
    
    return "Order metadata Stored in Dynamodb Table"
    
    