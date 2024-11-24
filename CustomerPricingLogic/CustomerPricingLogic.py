import boto3
import json

client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    # Prepare the payload for the Messages API
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"""
You are an AI pricing assistant. Calculate the final price for the customer and determine their delivery type based on the following details:

Customer Details:
- Prime Membership: {event.get('customer_prime_member', 'No')}
- Delivery Address: {event.get('customer_delivery_address', 'N/A')}

Product Details:
- Base Price: {event['product_price']}
- Quantity: {event['product_quantity']}

Pricing Rules:
1. Prime members:
   - Receive a 10% discount on the total price.
   - Get express delivery by default.
2. Non-Prime members:
   - No discount.
   - Standard delivery.

Respond ONLY with a JSON object containing the following keys:
- final_price: The calculated final price as a string.
- delivery_type: The delivery type as a string (Express or Standard).
- discount_applied: The discount applied as a percentage (e.g., "10%").
"""
            }
        ],
        "max_tokens": 200,  # Adjust based on expected output size
        "anthropic_version": "bedrock-2023-05-31"  # Replace with the correct version for your Claude model
    }

    # Call the Messages API
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',  # Replace with your model ID
        body=json.dumps(payload),  # Pass the JSON payload
        contentType='application/json',  # Required for Messages API
        accept='application/json'  # Expect JSON response
    )

    # Parse the response
    model_output = json.loads(response['body'].read().decode('utf-8'))
    
   
    # Extract the assistant's response
    assistant_response = model_output['content'][0]['text']
    parsed_response = json.loads(assistant_response)  # Parse the JSON object from the AI's response
    # Add the pricing details to the event
    event['final_price'] = parsed_response.get('final_price', '0')
    event['delivery_type'] = parsed_response.get('delivery_type', 'Unknown')
    event['discount_applied'] = parsed_response.get('discount_applied', '0%')

    return event
