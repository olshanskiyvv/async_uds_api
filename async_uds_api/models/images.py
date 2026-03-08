from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ImageUploadUrlHeaders(BaseModel):
    content_type: List[str] = Field(
        alias="Content-Type",
        validation_alias="Content-Type",
        description="Array of allowed content-types.",
    )


class ImageUploadUrl(BaseModel):
    image_id: str = Field(
        alias="imageId",
        validation_alias="imageId",
        description="Image identifier. This value has to be attached to goods entity.",
    )
    url: str = Field(description="Presigned upload url.")
    method: str = Field(description="Http method name.")
    headers: Optional[ImageUploadUrlHeaders] = None
    expires: Optional[int] = Field(
        default=None,
        description="Expiration time in epoch milliseconds.",
    )
