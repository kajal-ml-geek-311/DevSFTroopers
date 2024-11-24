import boto3
import json

client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    # Prepare the input payload for the Messages API
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"""
You are an AI Dangerous Goods Specialist or Hazardous Materials (HazMat) Professional for logistics shipping. Classify whether a product is hazardous or non-hazardous based on global shipping safety standards. Do not include any explanation or reasoning. Only output "HAZARDOUS" or "NON-HAZARDOUS".

Product Details:
- Name: {event['product_name']}
- Specifications: {event['product_specifications']}
- Dimensions: {event['product_dimensions']}
- Weight: {event['product_weight']}
- Quantity: {event['product_quantity']}
"""
            }
        ],
        "max_tokens": 200,  # Maximum tokens to generate
        "anthropic_version": "bedrock-2023-05-31"  # Replace with the correct model version
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
    assistant_response = model_output['content'][0]['text']
    print(assistant_response)
    # Add hazard classification to the event
    event['hazard_classification'] = assistant_response
    return event
