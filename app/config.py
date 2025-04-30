import os

class Settings:
    # S3 (MinIO) config
    S3_ENDPOINT_URL = "http://localhost:9000"
    S3_BUCKET = "uploads"
    S3_ACCESS_KEY = "minio"
    S3_SECRET_KEY = "minio123"

    # DynamoDB config
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "dummy")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "dummy")
    DYNAMODB_REGION = "us-east-1"

    # CORS
    ALLOWED_ORIGINS = ["http://localhost:5173"]

settings = Settings()
