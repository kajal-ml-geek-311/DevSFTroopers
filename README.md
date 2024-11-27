##DevSFTroopers
DevSFTroopers is a repository designed to streamline backend operations by utilizing AWS Lambda functions for various business processes. It supports workflows like order management, carrier negotiation, pricing logic, and integration with AWS services such as S3, DynamoDB, SES, and SQS.
Table of Contents
Introduction
Features
Lambda Functionality Details
Folder Structure
Prerequisites
Setup and Deployment
Contributing
License
Introduction
This project offers a suite of AWS Lambda functions to automate backend operations. The repository focuses on simplifying order processing, pricing management, carrier negotiations, hazard classification, and more, leveraging serverless architecture.
Features
Serverless Functions:
Efficient backend logic implemented as AWS Lambda functions.
AWS Service Integration:
Seamless integration with S3, DynamoDB, SQS, and SES.
Modular Design:
Each functionality is encapsulated in its dedicated module.
Extensibility:
Easily customizable to accommodate new business requirements.
Lambda Functionality Details
1. Order Management
aws-exportedge-dev-order-detail-api-lambda: Retrieves detailed information about orders from an API.
aws-exportedge-dev-order-insert-dynamodb-table-lambda: Stores order data into a DynamoDB table for efficient querying and management.
aws-exportedge-dev-order-list-api-lambda: Lists all orders in the system, providing structured outputs for integration with other services.
aws-exportedge-dev-read-order-json-from-s3-lambda: Reads order JSON files stored in an S3 bucket and processes them for further action.
aws-exportedge-dev-store-ordermetadata-json-in-s3bucket-lambda: Stores metadata of orders in an S3 bucket, enabling efficient tracking and archiving.
2. Document Management
aws-exportedge-dev-store-order-docs-in-s3bucket-lambda: Uploads and organizes order-related documents in an S3 bucket.
aws-exportedge-dev-read-docs-from-s3-api-lambda: Fetches and reads stored documents from S3 for downstream processing or auditing.
3. Notification Management
aws-exportedge-dev-ses-notification-lambda: Sends notifications using AWS Simple Email Service (SES) to keep stakeholders informed about order statuses and updates.
4. Hazard Classification
HazardClassification: Classifies hazardous materials in orders to comply with safety and regulatory requirements.
5. Carrier Negotiation
NegotiationWithCarrier: Automates the negotiation process with carriers for pricing and logistics planning.
6. Pricing Management
CarrierPricing: Handles pricing calculations and adjustments for carrier services.
CustomerPricingLogic: Computes pricing for customers based on predefined rules and conditions.
7. Artifact Generation
GenerateArtifact: Automatically generates artifacts related to orders, such as invoices, reports, or other required documents.
8. Integration and Data Streaming
aws-exportedge-dev-push-ordersjson-to-sqsqueue-lambda: Pushes JSON order data to an SQS queue for asynchronous processing.
aws-exportedge-dev-read-dynamodb-stream-lambda: Processes DynamoDB streams to capture changes in real-time for downstream workflows.
NeptuneIntegrationFunction-74fc2a7e-bbb5-4309-90a1-6560f88041c9: Integrates with Amazon Neptune to manage and query graph-based data for advanced analytics.
Folder Structure
The repository is structured as follows:
plaintextCopy code├── CarrierPricing/
├── CustomerPricingLogic/
├── ExtractOrderDetails/
├── GenerateArtifact/
├── HazardClassification/
├── NegotiationWithCarrier/
├── NeptuneIntegrationFunction-74fc2a7e-bbb5-4309-90a1-6560f88041c9/
├── aws-exportedge-dev-order-detail-api-lambda/
├── aws-exportedge-dev-order-insert-dynamodb-table-lambda/
├── aws-exportedge-dev-order-list-api-lambda/
├── aws-exportedge-dev-push-ordersjson-to-sqsqueue-lambda/
├── aws-exportedge-dev-read-docs-from-s3-api-lambda/
├── aws-exportedge-dev-read-dynamodb-stream-lambda/
├── aws-exportedge-dev-read-order-json-from-s3-lambda/
├── aws-exportedge-dev-ses-notification-lambda/
├── aws-exportedge-dev-store-order-docs-in-s3bucket-lambda/
├── aws-exportedge-dev-store-ordermetadata-json-in-s3bucket-lambda/
└── .DS_Store
Prerequisites
AWS Environment:
Active AWS account with IAM roles configured for Lambda functions.
Software:
Python (>= 3.7)
AWS CLI installed and configured.
Permissions:
Required permissions to access S3, DynamoDB, SQS, SES, and Lambda.
Setup and Deployment
Clone the Repository:
Setup AWS Environment: Ensure the AWS CLI is configured with necessary permissions:
Deploy Lambda Functions: Use AWS CLI, AWS SAM, or the Serverless Framework to deploy:
Test Lambda Functions: Invoke functions using the AWS CLI or AWS Lambda Console.
