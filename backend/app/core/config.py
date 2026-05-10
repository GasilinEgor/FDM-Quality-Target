import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "photos"
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY")


settings = Settings()