from fastapi import FastAPI, UploadFile, File, Forms, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import validate_image
import uuid
import shutil
import os
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-photo", response_model=PhotoResponse)
async def upload_photo(
    image: UploadFile = File(...),
    printer: str = Form(...),
    polymer_type: str = Form(...),
    polymer_color: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if not validate_image(image.content_type):
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    siffix = Path(image.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{siffix}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(image.file, f)
    
    photo = Photo(
        filename=filename,
        file_size=image.file.size,
        polymer_type=polymer_type,
        polymer_color=polymer_color,
        printer=printer,
    )
    db_photo = await create_photo_crud(photo, db)
    return db_photo