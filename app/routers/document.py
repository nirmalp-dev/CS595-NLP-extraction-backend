import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query

from app.config import settings
from app.document.download import get_file_content
from app.models import FileModel, ResultModel
from app.openai import summarize_text_with_openai
from app.storage import s3_client, FILES_TABLE, SUMMARY_TABLE

router = APIRouter(prefix="/document", tags=["Upload"])

ALLOWED_EXTENSIONS = {".txt", ".pdf"}

def allowed_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", summary="Upload TXT or PDF file to S3")
async def upload_file(file: UploadFile = File(...), username: str = "anonymous"):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are allowed")
    try:
        # Upload to S3
        file_uuid = str(uuid.uuid4())
        # Upload to S3/MinIO with custom metadata
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            file.filename,
            ExtraArgs={
                "Metadata": {
                    "uuid": file_uuid,
                    "uploader": username,
                    "filename": file.filename,
                },
                "ContentType": file.content_type
            }
        )
        # Add metadata to DynamoDB
        file_record = FileModel(
            uuid=file_uuid,
            filename=file.filename,
            uploaded_at=datetime.now().isoformat(),
            uploader=username,
            status="uploaded",
            content_type=file.content_type
        )
        # Add metadata to DynamoDB
        FILES_TABLE.put_item(Item=file_record.model_dump())
        return file_record
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/", summary="List all uploaded files")
async def list_uploaded_files():
    try:
        response = FILES_TABLE.scan()
        items = response.get("Items", [])
        files = [FileModel(**item) for item in items]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_document(request: Request):
    payload = await request.json()
    print("request to process document: ", payload)
    try:
        record = payload["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        metadata = record["s3"]["object"]["userMetadata"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid event structure")
    try:
        file_content = get_file_content(bucket, key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")
    # Get structured analysis from OpenAI
    analysis_result = summarize_text_with_openai(file_content)
        
    # Extract individual fields from the returned dictionary
    summary = analysis_result.get("summary", "")
    conditions = analysis_result.get("conditions", [])
    severity = analysis_result.get("severity", "")

    # summary = None
    doc_uuid = metadata.get("X-Amz-Meta-Uuid")
    doc_filename = metadata.get("X-Amz-Meta-Filename")
    doc_uploader = metadata.get("X-Amz-Meta-Uploader")
    if not doc_uuid:
        raise HTTPException(status_code=400, detail="UUID not found in metadata")

    # Then create the result record with the individual fields
    result_record = ResultModel(
        uuid=doc_uuid,
        filename=doc_filename,
        summary=summary,
        conditions=conditions,
        severity=severity,
    processed_at=datetime.now().isoformat()
)
    try:
        SUMMARY_TABLE.put_item(Item=result_record.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save summary: {e}")

    # Update status in files table
    try:
        FILES_TABLE.update_item(
            Key={"uuid": doc_uuid},
            UpdateExpression="SET #s = :s, processed_at = :t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "processed", ":t": datetime.now().isoformat()}
        )
        print("Document processed successfully! uuid: ", doc_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file status: {e}")

    return result_record

@router.get("/result", response_model=ResultModel)
async def get_result(uuid: str = Query(..., description="Document UUID")):
    try:
        response = SUMMARY_TABLE.get_item(Key={"uuid": uuid})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail=f"No result found for uuid: {uuid}")
        return ResultModel(**item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
