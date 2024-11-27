import boto3
import json
import time
from botocore.exceptions import ClientError
from decimal import Decimal

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

def calculate_benchmark_price(shipment_details):
    """
    Calculate benchmark prices based on shipment details.
    In a real implementation, this would use historical data and market rates.
    """
    weight = float(shipment_details.get('weight', 0))
    distance = float(shipment_details.get('distance', 0))
    service_level = shipment_details.get('service_level', 'standard')
    
    # Basic price calculation (would be more sophisticated in production)
    base_rate = 0.50  # per mile
    weight_rate = 0.75  # per pound
    
    # Service level multipliers
    service_multipliers = {
        'standard': 1.0,
        'express': 1.5,
        'priority': 2.0
    }
    
    multiplier = service_multipliers.get(service_level.lower(), 1.0)
    
    benchmark_price = (base_rate * distance + weight_rate * weight) * multiplier
    return round(benchmark_price, 2)

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

        # Extract shipment details and negotiation context
        shipment_details = body.get('shipment_details', {})
        current_quotes = body.get('current_quotes', [])
        negotiation_history = body.get('negotiation_history', [])
        target_price = body.get('target_price')
        is_retrying = body.get('is_retrying', False)

        if not shipment_details:
            raise ValueError("Shipment details are required.")

        # Calculate benchmark price
        benchmark_price = calculate_benchmark_price(shipment_details)

        # Enhanced Prompt for price negotiation
        prompt = f"""
You are a logistics pricing expert helping users negotiate carrier rates.

Shipment Details:
- Weight: {shipment_details.get('weight')} lbs
- Distance: {shipment_details.get('distance')} miles
- Service Level: {shipment_details.get('service_level')}
- Special Requirements: {shipment_details.get('special_requirements', 'None')}

Current Quotes:
{json.dumps(current_quotes, indent=2)}

Negotiation History:
{json.dumps(negotiation_history, indent=2)}

Target Price: ${target_price if target_price else 'Not specified'}
Benchmark Price: ${benchmark_price}

Please provide:
1. Analysis of current quotes vs. market rates
2. Specific negotiation strategies and talking points
3. Recommended counter-offer range
4. Key leverage points for negotiation

Format your response using Markdown for clarity.
Note: Consider current market conditions and carrier-specific factors in your analysis.
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

        # Generate market insights and recommendations
        market_data = {
            "benchmark_price": benchmark_price,
            "market_analysis": {
                "average_market_rate": benchmark_price * 1.1,  # Example calculation
                "lowest_market_rate": benchmark_price * 0.9,
                "highest_market_rate": benchmark_price * 1.3,
                "price_trends": "stable",  # Could be "rising", "falling", "stable"
                "market_conditions": "competitive"
            },
            "carrier_performance_metrics": {
                "on_time_delivery": "95%",
                "claims_ratio": "0.5%",
                "service_score": 4.2
            },
            "negotiation_recommendations": {
                "suggested_counter_offer": benchmark_price * 0.95,
                "target_range": {
                    "min": benchmark_price * 0.9,
                    "max": benchmark_price * 1.05
                },
                "key_leverage_points": [
                    "Volume commitment",
                    "Long-term contract",
                    "Payment terms",
                    "Service level flexibility"
                ]
            }
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
                "market_data": market_data,
                "benchmark_price": benchmark_price,
                "is_retrying": is_retrying
            }, cls=DecimalEncoder)  # Use custom encoder for Decimal objects
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

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)
