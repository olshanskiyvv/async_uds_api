from __future__ import annotations

from pydantic import Field

from async_uds_api.models.base import APIModel


class ImageUploadUrlHeaders(APIModel):
    content_type: list[str] = Field(
        alias="Content-Type",
        validation_alias="Content-Type",
        description="Array of allowed content-types.",
    )


class ImageUploadUrl(APIModel):
    image_id: str = Field(
        alias="imageId",
        validation_alias="imageId",
        description=(
            "Image identifier. This value has to be attached to goods entity."
        ),
    )
    url: str = Field(description="Presigned upload url.")
    method: str = Field(description="Http method name.")
    headers: ImageUploadUrlHeaders | None = None
    expires: int | None = Field(
        default=None,
        description="Expiration time in epoch milliseconds.",
    )
