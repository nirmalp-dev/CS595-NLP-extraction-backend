from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.responses import JSONResponse
import os
from app.storage import s3_client, FILES_TABLE
from app.config import settings

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
        s3_client.upload_fileobj(file.file, settings.S3_BUCKET, file.filename)
        # Add metadata to DynamoDB
        FILES_TABLE.put_item(Item={
            "filename": file.filename,
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploader": username,
            "content_type": file.content_type
        })
        return JSONResponse({"message": f"File '{file.filename}' uploaded and recorded."})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/", summary="List all uploaded files")
async def list_uploaded_files():
    try:
        response = FILES_TABLE.scan()
        items = response.get("Items", [])
        return {"files": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

