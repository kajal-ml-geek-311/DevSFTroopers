import json
import boto3

# DynamoDb Client Initialization
dynamodb_client = boto3.client("dynamodb")

# Dynamodb Table
dynamodb_table = "aws-exportedge-dev-order-dynamodb-table"


# Get Order Details
def get_order_details(order_id):

    order = {}
    
    update_dynamodbtable(order_id)
    
    response = dynamodb_client.get_item(
        TableName=dynamodb_table,
        Key={
            'order_id': {'S': order_id}
        }
    )
    
    order["order_id"] = response['Item']['order_id']['S']
    order["order_placed_timestamp"] = response['Item']['order_placed_timestamp']['S']
    order["product_name"] = response['Item']['product_name']['S']
    order["product_category"] = response['Item']['product_category']['S']
    order["product_price"] = response['Item']['product_price']['S']
    order["product_specifications"] = response['Item']['product_specifications']['S']
    order["product_dimensions"] = response['Item']['product_dimensions']['S']
    order["product_weight"] = response['Item']['product_weight']['S']
    order["product_quantity"] = response['Item']['product_quantity']['S']
    order["product_sku_id"] = response['Item']['product_sku_id']['S']
    order["customer_prime_member"] = response['Item']['customer_prime_member']['S']
    order["customer_mobile_number"] = response['Item']['customer_mobile_number']['S']
    order["customer_email_adress"] = response['Item']['customer_email_adress']['S']
    order["customer_delivery_address"] = response['Item']['customer_delivery_address']['S']
    order["warehouse_pickup_address"] = response['Item']['warehouse_pickup_address']['S']
    order["compliance_status"] = response['Item']['compliance_status']['S']
    order["order_status"] = response['Item']['order_status']['S']
    
    order_details = {
        "body": str(order)
    }

    print("order details")
    print(order)

    return order_details
    

# Update Order status in DynamoDb table as InProgress
def update_dynamodbtable(order_id):
    
    table = boto3.resource('dynamodb').Table(dynamodb_table)

    table.update_item(
        Key={'order_id': order_id},
        UpdateExpression="set #order_status = :order_status",
        ExpressionAttributeNames={
            "#order_status": "order_status",
        },
        ExpressionAttributeValues={
            ":order_status": "InProgress",
        },
        ReturnValues="UPDATED_NEW"
    )

    
def lambda_handler(event, context):
    
    print("event")
    print(event)

    order_id = event['path'].split("/")[2]
    order_details = get_order_details(order_id)

    print("Order Details retreived succusfully")
    return order_details