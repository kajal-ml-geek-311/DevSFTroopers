import boto3
import json

client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    # Extract necessary details from the event

    # Prepare the payload for the Messages API
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"""
You are an AI carrier assistant. Retrieve shipping options from the following carriers: DHL, FedEx, UPS and Bluedart only. Provide all possible options based on the following details:
Price should range from 50RS to 1000RS only.And we are dealing with Electronics products only.
We are shipping to three locations only USA,Australia and UK.
Order Details:
- Product Dimensions: {event['product_dimensions']}
- Product Weight: {event['product_weight']}
- Pickup Address: {event['warehouse_pickup_address']}
- Delivery Address: {event['customer_delivery_address']}
- Prime Member: {event['customer_prime_member']}
- Hazard Classification: {event['hazard_classification']}

Shipping Options Needed:
1. Cost-effective option.
2. Balanced option (cost and speed).
3. Urgent delivery option.
4. Best Option.

Considerations:
- If the product is HAZARDOUS, account for additional costs, restricted transportation modes, and extended delivery times.
- Prioritize low CO₂ emissions for all options.
- Provide realistic estimates for prices, delivery times, and environmental impact.

Respond ONLY with a well-formatted JSON object containing a list of shipping options with these keys:
- carrier: Name of the carrier (e.g., DHL, FedEx, UPS, Bluedart).
- option_type: One of "Cost-effective", "Balanced", "Urgent", or "Best Option".
- price: Price of the shipping as a string.
- delivery_time: Estimated delivery time as a string.
- co2_emissions: CO₂ emissions in kg as a string.
- mode: Transportation mode (Air or Sea only).

Do not include any additional text or explanations outside of the JSON object.
"""
            }
        ],
        "max_tokens": 400,  # Adjust based on expected output size
        "anthropic_version": "bedrock-2023-05-31"  # Replace with the correct version for your Claude model
    }

    # Call the Messages API
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',  # Replace with your actual model ID
        body=json.dumps(payload),  # Pass the JSON payload
        contentType='application/json',  # Required for Messages API
        accept='application/json'  # Expect JSON response
    )

    # Parse the response
    model_output = json.loads(response['body'].read().decode('utf-8'))

    # Extract the assistant's response
    assistant_response = model_output['content'][0]['text'].strip()

    # Ensure the assistant response is parsed as JSON
    try:
        parsed_response = json.loads(assistant_response)
    except json.JSONDecodeError:
        raise ValueError("The AI did not return a valid JSON response.")

    # Add the carrier pricing details to the event
    event['carrier_pricing'] = parsed_response
    return event
