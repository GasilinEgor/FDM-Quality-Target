ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/jpg",
}


def validate_image(content_type: str | None) -> bool:
    return bool(content_type and content_type.lower() in ALLOWED_IMAGE_TYPES)
