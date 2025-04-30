from fastapi import APIRouter, HTTPException
from app.models import UserCreate, UserLogin
from app.auth import hash_password, verify_password
from app.storage import USER_TABLE

router = APIRouter(prefix="", tags=["User"])

def get_user(username: str):
    response = USER_TABLE.get_item(Key={"username": username})
    return response.get("Item")

@router.post("/signup", status_code=201)
def signup(user: UserCreate):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    USER_TABLE.put_item(Item={
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password)
    })
    return {"msg": "User created successfully"}

@router.post("/login")
def login(user: UserLogin):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"msg": "Login successful"}
