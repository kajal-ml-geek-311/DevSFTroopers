import boto3
import json
import time
from botocore.exceptions import ClientError

# Initialize Bedrock client
client = boto3.client('bedrock-runtime')

def invoke_with_retries(payload, model_id, max_retries=3):
    attempt = 0
    while attempt <= max_retries:
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait_time = min(2 ** attempt, 5)
                print(f"ThrottlingException: Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                raise e
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

    raise Exception("Max retries exceeded due to ThrottlingException or connection issues.")

def lambda_handler(event, context):
    try:
        # Log the raw event for debugging
        print("Raw Event Received:", json.dumps(event))

        # Parse the request body
        if "body" in event:
            try:
                body = json.loads(event["body"])
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in the request body.")
        else:
            body = event

        # Extract tracking details and query type
        tracking_number = body.get('tracking_number', '').strip()
        order_id = body.get('order_id', '').strip()
        query_type = body.get('query_type', 'status').strip()  # status, eta, location, etc.
        carrier = body.get('carrier', '').strip()  # UPS, FedEx, DHL, etc.
        is_retrying = body.get('is_retrying', False)

        if not (tracking_number or order_id):
            raise ValueError("Either tracking number or order ID is required.")

        # Enhanced Prompt with specific tracking instructions
        prompt = f"""
You are a shipment tracking assistant helping users track their packages and orders. 
Respond to queries about shipment status, estimated delivery times, and current location.

Context:
- Tracking Number: {tracking_number if tracking_number else 'Not provided'}
- Order ID: {order_id if order_id else 'Not provided'}
- Carrier: {carrier if carrier else 'Not specified'}
- Query Type: {query_type}

When responding:
- Provide structured information about the shipment/order status
- Include estimated delivery dates when available
- List any potential delays or issues
- Suggest next steps or actions if needed
- Format the response using Markdown for clarity

Please respond with tracking information and status updates in a clear, structured format.
Note: In a real implementation, this would be integrated with actual carrier APIs for live tracking data.
        """

        # Prepare the payload for the Bedrock model
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "anthropic_version": "bedrock-2023-05-31"
        }

        # Invoke the Bedrock model with retries
        response = invoke_with_retries(payload, model_id='anthropic.claude-3-5-sonnet-20240620-v1:0')

        # Parse the response body
        response_body = response['body'].read().decode('utf-8')
        print("Decoded Bedrock Response Body:", response_body)

        model_output = json.loads(response_body)

        # Extract content from the response
        if 'content' not in model_output or not model_output['content']:
            raise ValueError(f"'content' key not found in the Bedrock response or it is empty: {model_output}")

        # Extract and return the assistant's response
        assistant_response = model_output['content'][0].get('text', '').strip()
        if not assistant_response:
            raise ValueError("AI response content is empty.")

        # Add mock tracking data (in a real implementation, this would come from carrier APIs)
        tracking_data = {
            "status": "in_transit",
            "last_update": "2024-11-27T10:30:00Z",
            "current_location": "Memphis, TN",
            "estimated_delivery": "2024-11-29",
            "tracking_events": [
                {
                    "timestamp": "2024-11-27T10:30:00Z",
                    "location": "Memphis, TN",
                    "status": "Arrived at sort facility"
                }
            ]
        }

        # Construct and return the API response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "response": assistant_response,
                "tracking_data": tracking_data,
                "is_retrying": is_retrying
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "error": str(e),
                "retry_allowed": not is_retrying
            })
        }
