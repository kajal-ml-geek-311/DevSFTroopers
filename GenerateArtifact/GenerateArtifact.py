import boto3
import json

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Flatten the input event to extract the string values
        flattened_event = {}
        for key, value in event.items():
            if isinstance(value, dict) and 'S' in value:
                # For DynamoDB-style entries
                flattened_event[key] = value['S']
            else:
                # For regular JSON entries or nested dictionaries
                flattened_event[key] = value
        
        # Validate required keys in the flattened event
        required_keys = [
            "order_id", "product_name", "customer_delivery_address", 
            "product_weight", "product_quantity", "product_price", 
            "product_dimensions", "product_specifications", 
            "warehouse_pickup_address", "customer_prime_member"
        ]
        
        missing_keys = [key for key in required_keys if key not in flattened_event]
        if missing_keys:
            raise KeyError(f"Missing required keys: {missing_keys}")
        
        # Prepare the summary for artifact generation
        summary = {
            "order_id": flattened_event['order_id'],
            "product_name": flattened_event['product_name'],
            "customer_delivery_address": flattened_event['customer_delivery_address'],
            "product_weight": flattened_event['product_weight'],
            "product_quantity": flattened_event['product_quantity'],
            "product_price": flattened_event['product_price'],
            "product_dimensions": flattened_event['product_dimensions'],
            "product_specifications": flattened_event['product_specifications'],
            "warehouse_pickup_address": flattened_event['warehouse_pickup_address'],
            "customer_prime_member": flattened_event['customer_prime_member'],
            "hazard_classification": flattened_event.get('hazard_classification', 'Unknown'),
            "carrier_pricing": flattened_event.get('carrier_pricing', {}),
            "negotiated_prices": flattened_event.get('negotiated_prices', {}),
            "chat": flattened_event.get('chat', {}),
            "recommendations":flattened_event.get('recommendation', {})

        }
        
        # Save the summary as an artifact in the S3 bucket
        artifact_key = f"artifacts/{flattened_event['order_id']}.json"
        print(f"Saving artifact to: {artifact_key}")
        s3_client.put_object(
            Bucket='seller-carrier-output-bucket',
            Key=artifact_key,
            Body=json.dumps(summary)
        )
        
        # Add the artifact URL to the summary
        summary['artifact_url'] = f"s3://seller-carrier-output-bucket/{artifact_key}"
        return summary

    except KeyError as e:
        return {
            "status": "error",
            "message": f"KeyError: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
