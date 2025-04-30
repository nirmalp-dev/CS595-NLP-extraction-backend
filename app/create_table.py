import boto3

# Connect to DynamoDB Local (adjust the endpoint URL/port if needed)
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy",
    endpoint_url="http://localhost:8000"  # Use your DynamoDB Local port
)

# Table definitions: name and key schema
tables = [
    {
        "name": "users",
        "key_schema": [
            {'AttributeName': 'username', 'KeyType': 'HASH'}
        ],
        "attribute_definitions": [
            {'AttributeName': 'username', 'AttributeType': 'S'}
        ]
    },
    {
        "name": "file",
        "key_schema": [
            {'AttributeName': 'uuid', 'KeyType': 'HASH'}
        ],
        "attribute_definitions": [
            {'AttributeName': 'uuid', 'AttributeType': 'S'}
        ]
    },
    {
        "name": "document_results",
        "key_schema": [
            {'AttributeName': 'uuid', 'KeyType': 'HASH'}
        ],
        "attribute_definitions": [
            {'AttributeName': 'uuid', 'AttributeType': 'S'}
        ]
    }
]

# Create tables if they do not exist
existing_tables = [table.name for table in dynamodb.tables.all()]
for tbl in tables:
    if tbl["name"] not in existing_tables:
        print(f"Creating table '{tbl['name']}'...")
        table = dynamodb.create_table(
            TableName=tbl["name"],
            KeySchema=tbl["key_schema"],
            AttributeDefinitions=tbl["attribute_definitions"],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print(f"Table '{tbl['name']}' created!")
    else:
        print(f"Table '{tbl['name']}' already exists.")
