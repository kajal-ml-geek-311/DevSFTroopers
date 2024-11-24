import json
import boto3

# SES Client Initialization
ses_client = boto3.client("ses")

# Email Configuartion's
sender_email = 'suraj.paratrooper@gmail.com'
recipient_email = 'suraj.parasf21@gmail.com'


# Send Email notification to consumer abt Order couldn't be Placed
def send_email(email_subject, email_body):
    
    response = ses_client.send_email(
        Source=sender_email,
        Destination={
            'ToAddresses': [recipient_email],
            'CcAddresses': [],
            'BccAddresses': []
        },
        Message={
            'Subject': {
                'Data': email_subject
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
    )
    

    print("Notification Email sent successfully")


def lambda_handler(event, context):
    
    print("event")
    print(event)
    
    email_subject = f"Notification : Order with OrderID : {event['order_id']} couldn't be Placed"
    email_body = "Order is non Complaint with Regulations of USA country , so it cannot be placed"
    
    send_email(email_subject, email_body)
    
    return "Notification Email sent successfully"
