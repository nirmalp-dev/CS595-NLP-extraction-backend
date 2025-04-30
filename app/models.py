from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# --- User Models ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# --- File Metadata Model ---
class FileModel(BaseModel):
    uuid: str
    filename: str
    uploaded_at: str
    uploader: str
    processed_at: Optional[str] = None
    status: Optional[str] = "uploaded"
    content_type: str

# --- Structured Medical Output Models ---
class Condition(BaseModel):
    name: str
    code: Optional[str] = None
    coding_system: Optional[str] = None

class LabResult(BaseModel):
    name: str
    value: str
    unit: str
    interpretation: Optional[str] = None
    loinc_code: Optional[str] = None

class Procedure(BaseModel):
    name: str
    cpt_code: Optional[str] = None

class Medication(BaseModel):
    name: str
    dose: Optional[str] = None
    route: Optional[str] = None
    rxnorm_code: Optional[str] = None

# --- Final Analysis Result Model ---
class ResultModel(BaseModel):
    uuid: str
    filename: str
    summary: Optional[str] = None
    severity: Optional[str] = None
    processed_at: Optional[str] = None
    conditions: List[Condition] = []
    labs: List[LabResult] = []
    procedures: List[Procedure] = []
    medications: List[Medication] = []
