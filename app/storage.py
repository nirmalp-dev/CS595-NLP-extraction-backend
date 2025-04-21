import boto3
from config import settings

# S3 client (MinIO)
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name="us-east-1",
)

# DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    region_name=settings.DYNAMODB_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.DYNAMODB_ENDPOINT,
)
USER_TABLE = dynamodb.Table("users")
FILES_TABLE = dynamodb.Table("file")