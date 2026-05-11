from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class PhotoBase(SQLModel):
    filename: str = Field(min_length=1)
    file_size: int
    polymer_type: str
    polymer_color: str
    printer: str

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None