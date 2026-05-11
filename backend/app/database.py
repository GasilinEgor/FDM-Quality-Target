from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session as SQLModelSession
from .models import engine  # Ваш engine из models.py

SQLModelSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> SQLModelSession:
    session = SQLModelSessionLocal()
    try:
        yield session
    finally:
        session.close()