from sqlmodel import select, Session
from .models import Photo, ProcessedPhoto, Defect
from typing import List, Dict, Any

async def create_photo(photo_data: Dict[str, Any], session: Session) -> Photo:
    photo = Photo(**photo_data)
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo

async def create_processed_photo(
    original_id: int, 
    processed_data: Dict[str, Any], 
    defects_data: List[Dict[str, Any]], 
    session: Session
) -> ProcessedPhoto:
    processed = ProcessedPhoto(original_id=original_id, **processed_data)
    session.add(processed)
    session.commit()
    session.refresh(processed)
    
    for defect_data in defects_data:
        defect = Defect(processed_photo_id=processed.id, **defect_data)
        session.add(defect)
    
    session.commit()
    return processed

async def get_photo_full(photo_id: int, session: Session):
    photo = session.get(Photo, photo_id)
    if not photo:
        return None
        
    processed = session.get(ProcessedPhoto, photo.processed_photo_id)
    if processed:
        defects = session.exec(
            select(Defect).where(Defect.processed_photo_id == processed.id)
        ).all()
    
    return {
        "photo": photo,
        "processed": processed,
        "defects": defects or []
    }