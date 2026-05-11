from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from ..crud import create_photo, create_processed_photo, get_photo_full
from ..database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/photos", tags=["photos"])

class PhotoCreate(BaseModel):
    s3_key: str
    filename_original: str
    plastic_type: str
    plastic_color: str
    printer_name: str

class DefectCreate(BaseModel):
    x: float
    y: float
    w: float
    h: float
    defect_type: str
    confidence: float

@router.post("/")
async def upload_photo(
    photo: PhotoCreate,
    session: Session = Depends(get_session)
):
    created = await create_photo(photo.dict(), session)
    return {"photo_id": created.id, "status": "pending"}

@router.post("/{photo_id}/processed/")
async def ai_processed(
    photo_id: int,
    processed_s3_key: str,
    defects: List[DefectCreate],
    session: Session = Depends(get_session)
):
    processed_data = {"s3_key": processed_s3_key}
    created = await create_processed_photo(photo_id, processed_data, [d.dict() for d in defects], session)
    return {"status": "processed"}

@router.get("/{photo_id}/")
async def get_photo(photo_id: int, session: Session = Depends(get_session)):
    result = await get_photo_full(photo_id, session)
    if not result:
        raise HTTPException(404, "Фото не найдено")
    return result