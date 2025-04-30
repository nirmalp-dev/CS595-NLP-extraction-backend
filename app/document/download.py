from app.storage import s3_client


def get_file_content(bucket: str, key: str) -> str:
    # Download the object into memory
    response = s3_client.get_object(Bucket=bucket, Key=key)
    body = response['Body'].read()
    # If it's a text file, decode as UTF-8
    return body.decode('utf-8')