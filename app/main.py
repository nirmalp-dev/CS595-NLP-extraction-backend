from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.storage import s3_client
from app.routers import user, document

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure S3 bucket exists
    existing_buckets = s3_client.list_buckets()
    if settings.S3_BUCKET not in [b['Name'] for b in existing_buckets.get('Buckets', [])]:
        s3_client.create_bucket(Bucket=settings.S3_BUCKET)
    yield

app = FastAPI(
    title="My API",
    description="API for user management and file upload",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(document.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)