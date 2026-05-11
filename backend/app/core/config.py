from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    S3_ENDPOINT: str
    S3_REGION: str 
    S3_BUCKET: str 
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str

    DATABASE_URL: str


    model_config = SettingsConfigDict(
    env_file=ENV_FILE,\
    env_file_encoding="utf-8"
)
settings = Settings()

# Отладка
print(f".env путь: {ENV_FILE}")
print(f"S3_BUCKET: {settings.S3_BUCKET}")
print(f"Ключи загружены: {'cool' if settings.S3_ACCESS_KEY_ID else 'baaaad'}")