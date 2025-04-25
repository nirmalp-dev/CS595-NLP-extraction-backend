from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class FileModel(BaseModel):
    uuid: str
    filename: str
    uploaded_at: str
    uploader: str
    processed_at: Optional[str] = None
    status: Optional[str] = "uploaded"
    content_type: str

class ResultModel(BaseModel):
    uuid: str
    filename: str
    summary: Optional[str] = None
    processed_at: str