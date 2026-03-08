import mimetypes
import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import aiofiles
import httpx

from async_uds_api.errors import (
    UDSImageDownloadError,
    UDSImageReadError,
    UDSImageUnsupportedSourceError,
    UDSImageUploadError,
)
from async_uds_api.models import ImageUploadUrl

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class ImagesAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client
        self._upload_client: httpx.AsyncClient | None = None

    async def _get_upload_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for image uploads."""
        if self._upload_client is None:
            self._upload_client = httpx.AsyncClient()
        return self._upload_client

    async def _close_upload_client(self) -> None:
        """Close the upload HTTP client."""
        if self._upload_client is not None:
            await self._upload_client.aclose()
            self._upload_client = None

    async def get_upload_url(self, content_type: str) -> ImageUploadUrl:
        """
        Get presigned URL for image upload.

        Args:
            content_type: Image content type (e.g., "image/jpeg")

        Returns:
            ImageUploadUrl with image_id, url, method, headers, expires

        Raises:
            UDSImageUnsupportedSourceError: If content_type is not a valid MIME type
        """
        self._validate_content_type(content_type)

        body = {"contentType": content_type}
        data = await self._client._post_json("/image-upload-url", body=body)
        return ImageUploadUrl.model_validate(data)

    async def upload(
        self,
        source: str | Path | bytes,
        content_type: str | None = None,
    ) -> str:
        """
        Upload image and return image_id.

        This method:
        1. Validates content_type (if provided)
        2. Detects content type if not provided (for str/Path sources)
        3. Reads image data (from file path, URL, or bytes)
        4. Gets presigned URL via get_upload_url()
        5. Uploads image to the presigned URL
        6. Returns image_id for use in goods.photos

        Args:
            source: Path to image file, URL to image, or image bytes
            content_type: Image content type (e.g., "image/jpeg").
                         Required if source is bytes.
                         If None for str/Path, will be detected automatically.

        Returns:
            image_id to use in goods.photos

        Raises:
            UDSImageReadError: If file cannot be read
            UDSImageDownloadError: If image cannot be downloaded from URL
            UDSImageUploadError: If upload to presigned URL fails
            UDSImageUnsupportedSourceError: If source is not valid or content_type is invalid
        """
        if isinstance(source, bytes):
            if content_type is None:
                raise UDSImageUnsupportedSourceError(
                    "content_type is required when source is bytes"
                )
            self._validate_content_type(content_type)
        else:
            if content_type is not None:
                self._validate_content_type(content_type)
            else:
                content_type = self._detect_content_type(source)

        image_data = await self._read_image_data(source)

        upload_info = await self.get_upload_url(content_type)

        await self._upload_to_url(upload_info, image_data)

        return upload_info.image_id

    def _validate_content_type(self, content_type: str) -> None:
        """
        Validate content_type is a valid MIME type.

        Args:
            content_type: MIME type string (e.g., "image/jpeg")

        Raises:
            UDSImageUnsupportedSourceError: If content_type is not a valid MIME type
        """
        mime_pattern = (
            r"^[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+/[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+$"
        )

        if not re.match(mime_pattern, content_type):
            raise UDSImageUnsupportedSourceError(
                f"Invalid content_type format: '{content_type}'. "
                f"Expected format: 'type/subtype' (e.g., 'image/jpeg')"
            )

    def _detect_content_type(self, source: str | Path) -> str:
        """
        Detect content type from file path or URL.

        Args:
            source: File path or URL

        Returns:
            Detected MIME type or 'image/jpeg' as fallback
        """
        source_str = str(source)
        mime_type, _ = mimetypes.guess_type(source_str)

        if mime_type is None:
            return "image/jpeg"

        return mime_type

    async def _read_image_data(self, source: str | Path | bytes) -> bytes:
        """
        Read image data from file path, URL, or bytes.

        Args:
            source: File path, URL, or bytes

        Returns:
            Image binary data

        Raises:
            UDSImageReadError: If file cannot be read
            UDSImageDownloadError: If image cannot be downloaded from URL
        """
        if isinstance(source, bytes):
            return source

        source_str = str(source)

        parsed = urlparse(source_str)
        if parsed.scheme in ("http", "https"):
            return await self._download_from_url(source_str)

        return await self._read_from_file(Path(source))

    async def _read_from_file(self, path: Path) -> bytes:
        """
        Read image data from file.

        Args:
            path: Path to image file

        Returns:
            Image binary data

        Raises:
            UDSImageReadError: If file cannot be read
        """
        if not path.exists():
            raise UDSImageReadError(f"File not found: {path}")

        try:
            async with aiofiles.open(path, "rb") as f:
                return await f.read()
        except Exception as e:
            raise UDSImageReadError(f"Failed to read file {path}: {e}") from e

    async def _download_from_url(self, url: str) -> bytes:
        """
        Download image from URL.

        Args:
            url: URL to download image from

        Returns:
            Image binary data

        Raises:
            UDSImageDownloadError: If image cannot be downloaded
        """
        client = await self._get_upload_client()

        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise UDSImageDownloadError(
                f"Failed to download image from {url}: {e}"
            ) from e

    async def _upload_to_url(
        self,
        upload_info: ImageUploadUrl,
        image_data: bytes,
    ) -> None:
        """
        Upload image data to presigned URL.

        Args:
            upload_info: Upload URL info from get_upload_url()
            image_data: Image binary data

        Raises:
            UDSImageUploadError: If upload fails
        """
        client = await self._get_upload_client()

        headers = {}
        if upload_info.headers and upload_info.headers.content_type:
            headers["Content-Type"] = upload_info.headers.content_type[0]

        try:
            if upload_info.method.upper() == "PUT":
                response = await client.put(
                    upload_info.url,
                    content=image_data,
                    headers=headers,
                )
            elif upload_info.method.upper() == "POST":
                response = await client.post(
                    upload_info.url,
                    content=image_data,
                    headers=headers,
                )
            else:
                raise UDSImageUploadError(
                    f"Unsupported upload method: {upload_info.method}"
                )

            response.raise_for_status()
        except Exception as e:
            raise UDSImageUploadError(f"Failed to upload image: {e}") from e
