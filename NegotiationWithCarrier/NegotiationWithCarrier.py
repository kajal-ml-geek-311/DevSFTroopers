import boto3
import json
import re

client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    try:
        # Extract carrier pricing from the event
        carrier_pricing = event.get('carrier_pricing', {}).get('shipping_options', [])
        
        # Validate carrier_pricing structure
        if not isinstance(carrier_pricing, list):
            raise ValueError("carrier_pricing must be a list of dictionaries.")
        
        # Format the shipping options into a user-friendly list
        options = "\n".join([
            f"{idx + 1}. Carrier: {option.get('carrier', 'Unknown')}, Price: {option.get('price', 'Unknown')}, "
            f"Delivery Time: {option.get('delivery_time', 'Unknown')}, CO₂ Emissions: {option.get('co2_emissions', 'Unknown')}"
            for idx, option in enumerate(carrier_pricing)
            if isinstance(option, dict)  # Ensure each entry is a dictionary
        ])
        
        # Prepare the prompt with realistic rules and context
        prompt = f"""
You are an AI logistics negotiation assistant representing a seller. Negotiate individually with each carrier based on their shipping options, balancing cost, delivery speed, and environmental impact.

### Shipping Options:
{options}

### Key Details:
- Prime Membership: {'Yes' if event.get('customer_prime_member', {}).get('S', 'No') == 'Yes' else 'No'}.
- Hazard Classification: {event.get('hazard_classification', 'Unknown')}.
- Bulk Quantity: {event.get('product_quantity', {}).get('S', 'Unknown')} units.
- Sustainability Focus: Prefer carriers with lower CO₂ emissions for cost-effective and balanced options.

### Rules for Negotiation:
1. Negotiate individually with each carrier for better rates.
2. Consider discounts for bulk orders and Prime members.
3. Prioritize sustainability and cost-effective solutions.
4. Provide a detailed JSON response with:
   - negotiated_prices: List of carriers with original price, negotiated price, discount, and reasoning.
   - chat: Detailed multi-turn conversations for each carrier.
   - recommendation: Final recommendation based on cost, delivery time, and environmental impact.

### Negotiation Conversations:
- Start by asking for discounts based on bulk orders or Prime membership.
- Ask carriers to justify their costs for expedited shipping or sustainability-related emissions.
- Negotiate further if the provided rates are not competitive.
- Finalize each negotiation with explicit rates and reasoning.
**Provide only the JSON response with the following structure, enclosed in triple backticks and labeled as `json`, without any additional text:**

```json
{{
  "negotiated_prices": [...],
  "chat": {{...}},
  "recommendation": {{...}}
}}
"""
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 5000,  # Adjust if needed
            "anthropic_version": "bedrock-2023-05-31"  # Replace with the correct version
        }

        # Call the Messages API
        response = client.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',  # Replace with your actual model ID
            body=json.dumps(payload),  # Pass the JSON payload
            contentType='application/json',  # Required
            accept='application/json'  # Expect JSON response
        )

        # Parse the response
        model_output = json.loads(response['body'].read().decode('utf-8'))

        # Access the text content correctly
        if 'completion' in model_output:
            assistant_response = model_output['completion'].strip()
        elif 'content' in model_output and isinstance(model_output['content'], list):
            assistant_response = model_output['content'][0].get('text', '').strip()
        else:
            raise ValueError("The model output structure is unexpected or 'content' field is missing.")

        # Extract JSON code block from the assistant's response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', assistant_response, re.DOTALL)
        if not json_match:
            raise ValueError("The AI did not return a valid JSON response.")

        json_string = json_match.group(1).strip()
        def clean_json_string(s):
            # Remove newline characters
            #s = s.replace('\n', ' ')
            # Remove any control characters
            s = re.sub(r'[\x00-\x1F\x7F]', '', s)
            s = re.sub('        ',' ',s)
            s = re.sub('      ','',s)
            s = re.sub('    ',' ',s)
            s = re.sub('  ',' ',s)
            s = re.sub('} ] }','}]}',s)
            s = re.sub('} ]','}]',s)
            s = re.sub(r'\[ {', '[{', s)
            
            
            return s
        json_string_cleaned = clean_json_string(json_string)
        
        print(json_string_cleaned)
        
        print(json.loads(json_string_cleaned))
        # Attempt to parse the JSON string
        try:
            parsed_response = json.loads(json_string)
        except json.JSONDecodeError as e:
            # Log the error and the problematic strings
            print(f"Error decoding JSON: {str(e)}")
            print("Assistant Response:")
            print(assistant_response)
            print("Extracted JSON String:")
            print(json_string)
            raise ValueError(f"Error decoding JSON: {str(e)}")

        # Validate parsed_response structure
        if not isinstance(parsed_response, dict):
            raise ValueError("Parsed response is not a valid dictionary.")

        # Add the negotiated prices and chat to the event
        event['negotiated_prices'] = parsed_response.get('negotiated_prices', [])
        event['chat'] = parsed_response.get('chat', {})
        event['recommendation'] = parsed_response.get('recommendation', "No recommendation provided.")

        return event
    except Exception as e:
        # Log the error and return a response with the error message
        print(f"Error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }