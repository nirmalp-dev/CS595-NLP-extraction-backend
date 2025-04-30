import os
import tempfile
from app.storage import s3_client
from pdfminer.high_level import extract_text


def get_file_content(bucket: str, key: str) -> str:
    """
    Extract text from .txt or .pdf file stored in S3.
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content_type = response.get("ContentType", "")

        if content_type == "application/pdf" or key.lower().endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response["Body"].read())
                tmp_path = tmp_file.name

            try:
                text = extract_text(tmp_path)
                return text
            finally:
                os.remove(tmp_path)

        elif content_type == "text/plain" or key.lower().endswith(".txt"):
            return response["Body"].read().decode("utf-8")

        else:
            raise ValueError(f"Unsupported file type: {content_type}")

    except Exception as e:
        raise RuntimeError(f"Error while reading file from S3: {e}")
