import boto3
from botocore.config import Config
from botocore.client import BaseClient
from .core.config import settings


def get_s3_client() -> BaseClient:

    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
    )

