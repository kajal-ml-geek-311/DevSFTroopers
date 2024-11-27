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
            # Invoke Bedrock model
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait_time = min(2 ** attempt, 5)  # Exponential backoff capped at 5 seconds
                print(f"ThrottlingException: Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                raise e
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)  # 1-second delay between attempts
 
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
 
        # Extract user input, language, and retry state
        user_input = body.get('user_input', '').strip()
        user_language = body.get('language', 'en').strip()
        is_retrying = body.get('is_retrying', False)
 
        if not user_input:
            raise ValueError("Input message is empty.")
 
        # Enhanced Prompt with Markdown
        prompt = f"""
You are a compliance officer assisting Indian exporters with documentation for shipments to the USA, Australia, and the UK.
 
When responding to queries:
- Provide concise, pointwise answers.
- Use Markdown formatting for clarity. For example:
  - Use `**bold**` for headers or key points.
  - Use clickable links like `[link text](https://example.com)`.
- Separate mandatory and optional documents if applicable.
 
Now respond to the user's query in Markdown format. Example:
- **Document Name**: Brief description.
  - Link: [Click here for details](https://example.com)
 
Now respond to the user's query: {user_input}
        """
 
        # Prepare the payload for the Bedrock model
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,  # Limit response length for speed
            "anthropic_version": "bedrock-2023-05-31"  # Adjust Bedrock version
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
 
        # Construct and return the API response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # CORS headers
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "response": assistant_response,
                "is_retrying": is_retrying  # Inform the UI of retry state
            })
        }
 
    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # CORS headers
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "error": str(e),
                "retry_allowed": not is_retrying  # Prevent multiple retries in the UI
            })
        }
