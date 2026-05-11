from sqlmodel import SQLModel, Field, Relationship, create_engine
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from .core.config import settings
import asyncio

class Photo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    s3_key: str
    filename_original: str
    content_type: str
    file_size: int
    
    plastic_type: str = Field(max_length=50)
    plastic_color: str = Field(max_length=50)
    printer_name: str = Field(max_length=100)
    
    title: Optional[str] = Field(default="", max_length=200)
    
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    processed_photo_id: Optional[int] = None  

class Defect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    processed_photo_id: int = Field(foreign_key="processedphoto.id")
    x: float
    y: float  
    w: float
    h: float
    defect_type: str
    confidence: float

class ProcessedPhoto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_id: int = Field(foreign_key="photo.id")
    s3_key: str
    defects: List[Defect] = Relationship(back_populates="processed_photo")
    ai_confidence: float
    processed_at: datetime = Field(default_factory=datetime.now)

engine = create_engine(settings.DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_tables():
    SQLModel.metadata.create_all(engine)
    print("|||\/|||ТАблицы созданы!|||\/|||")


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

async def init_db():
    await asyncio.to_thread(create_db_tables)
