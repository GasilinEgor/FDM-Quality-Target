from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .core.security import validate_image
from .core.config import settings
from .schemas import PhotoResponse
from .models import Photo, create_db_tables, init_db
from app.routers.photos import router as photos_router
from .s3_service import get_s3_client
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import uuid
import shutil

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app = FastAPI(lifespan=lifespan)
app.include_router(photos_router)


async def get_db() -> AsyncGenerator[None, None]:
    yield None


async def create_photo_crud(photo: Photo, db: AsyncSession | None) -> Photo:
    photo.id = 1
    photo.created_at = datetime.now()
    return photo

@app.post("/upload-photo", response_model=PhotoResponse)
async def upload_photo(
    image: UploadFile = File(...),
    printer: str = Form(...),
    polymer_type: str = Form(...),
    polymer_color: str = Form(...),
    db: AsyncSession | None = Depends(get_db),
):
    if not validate_image(image.content_type):
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    suffix = Path(image.filename or "").suffix.lower()
    filename = f"{uuid.uuid4()}{suffix}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(image.file, f)
    
    photo = Photo(
        filename=filename,
        file_size=getattr(image, "size", 0) or 0,
        polymer_type=polymer_type,
        polymer_color=polymer_color,
        printer=printer,
    )
    db_photo = await create_photo_crud(photo, db)
    return db_photo


@app.get("/s3/test")
async def test_s3():
    try:
        s3_client = get_s3_client()
        s3_client.head_bucket(Bucket=settings.S3_BUCKET)
        return {"status": "OK", "bucket": settings.S3_BUCKET}
    except Exception as e:
        raise HTTPException(500, str(e))