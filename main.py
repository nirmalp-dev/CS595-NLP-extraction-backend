import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import boto3
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DynamoDB setup (swap endpoint_url for local/production)
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")  # Local DynamoDB
)
USER_TABLE = dynamodb.Table("users")

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    response = USER_TABLE.get_item(Key={"username": username})
    return response.get("Item")


@app.post("/signup", status_code=201)
def signup(user: UserCreate):
    # Check if user exists
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash password and store user
    USER_TABLE.put_item(Item={
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password)
    })
    return {"msg": "User created successfully"}

@app.post("/login")
def login(user: UserLogin):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # No tokens, just confirmation
    return {"msg": "Login successful"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
