from pydantic import BaseModel
from typing import Optional
from models import Photo

class PhotoResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    polymer_type: str
    polymer_color: str
    printer: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PhotoList(BaseModel):
    photos: list[PhotoResponse]
    total: int