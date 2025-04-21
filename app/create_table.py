import boto3

# Connect to DynamoDB Local (adjust the endpoint URL/port if needed)
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy",
    endpoint_url="http://localhost:8000"  # Use your DynamoDB Local port
)

# Create the 'users' table if it doesn't exist
table_name = "users"
existing_tables = [table.name for table in dynamodb.tables.all()]
if table_name not in existing_tables:
    print(f"Creating table '{table_name}'...")
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'username', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'username', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print(f"Table '{table_name}' created!")
else:
    print(f"Table '{table_name}' already exists.")

table_name = "file"
existing_tables = [table.name for table in dynamodb.tables.all()]
if table_name not in existing_tables:
    print(f"Creating table '{table_name}'...")
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'filename', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'filename', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print(f"Table '{table_name}' created!")
else:
    print(f"Table '{table_name}' already exists.")