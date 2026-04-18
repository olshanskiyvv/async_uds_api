import logging
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

_logger = logging.getLogger("async_uds_api")

_MIME_RE = re.compile(
    r"^[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+/[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+$"
)


class ImagesAPI:
    def __init__(self, client: "UDSClient", timeout: float) -> None:
        self._client = client
        self._timeout = timeout
        self._upload_client = httpx.AsyncClient(timeout=timeout)

    async def _close_upload_client(self) -> None:
        await self._upload_client.aclose()

    async def get_upload_url(self, content_type: str) -> ImageUploadUrl:
        self._validate_content_type(content_type)
        _logger.debug(
            "Requesting upload URL for content_type=%s", content_type
        )
        body = {"contentType": content_type}
        data = await self._client._post_json("/image-upload-url", body=body)
        result = ImageUploadUrl.model_validate(data)
        _logger.info("Got upload URL: image_id=%s", result.image_id)
        return result

    async def upload(
        self,
        source: str | Path | bytes,
        content_type: str | None = None,
    ) -> str:
        if isinstance(source, bytes):
            if content_type is None:
                raise UDSImageUnsupportedSourceError(
                    "content_type is required when source is bytes"
                )
            self._validate_content_type(content_type)
            _logger.debug(
                "Uploading %d bytes with content_type=%s",
                len(source),
                content_type,
            )
        else:
            if content_type is not None:
                self._validate_content_type(content_type)
            else:
                content_type = self._detect_content_type(source)
            _logger.debug(
                "Uploading from %s with content_type=%s", source, content_type
            )

        image_data = await self._read_image_data(source)
        _logger.debug("Read %d bytes", len(image_data))

        upload_info = await self.get_upload_url(content_type)
        await self._upload_to_url(upload_info, image_data)

        _logger.info(
            "Image uploaded successfully: image_id=%s", upload_info.image_id
        )
        return upload_info.image_id

    def _validate_content_type(self, content_type: str) -> None:
        if not _MIME_RE.match(content_type):
            raise UDSImageUnsupportedSourceError(
                f"Invalid content_type format: '{content_type}'. "
                f"Expected format: 'type/subtype' (e.g., 'image/jpeg')"
            )

    def _detect_content_type(self, source: str | Path) -> str:
        source_str = str(source)
        mime_type, _ = mimetypes.guess_type(source_str)
        if mime_type is None:
            raise UDSImageUnsupportedSourceError(
                f"Cannot detect content type for '{source_str}'. "
                "Provide content_type explicitly."
            )
        return mime_type

    async def _read_image_data(self, source: str | Path | bytes) -> bytes:
        if isinstance(source, bytes):
            return source

        source_str = str(source)
        parsed = urlparse(source_str)
        if parsed.scheme in ("http", "https"):
            return await self._download_from_url(source_str)

        return await self._read_from_file(Path(source))

    async def _read_from_file(self, path: Path) -> bytes:
        _logger.debug("Reading image from file: %s", path)
        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
            _logger.debug("Read %d bytes from %s", len(data), path)
            return data
        except FileNotFoundError:
            _logger.error("File not found: %s", path)
            raise UDSImageReadError(f"File not found: {path}")
        except Exception as e:
            _logger.error("Failed to read file %s: %s", path, e)
            raise UDSImageReadError(f"Failed to read file {path}: {e}") from e

    async def _download_from_url(self, url: str) -> bytes:
        _logger.debug("Downloading image from URL: %s", url)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
            _logger.debug(
                "Downloaded %d bytes from %s", len(response.content), url
            )
            return response.content
        except Exception as e:
            _logger.error("Failed to download image from %s: %s", url, e)
            raise UDSImageDownloadError(
                f"Failed to download image from {url}: {e}"
            ) from e

    async def _upload_to_url(
        self,
        upload_info: ImageUploadUrl,
        image_data: bytes,
    ) -> None:
        headers = {}
        if upload_info.headers and upload_info.headers.content_type:
            headers["Content-Type"] = upload_info.headers.content_type[0]

        method = upload_info.method.upper()
        if method not in ("PUT", "POST"):
            raise UDSImageUploadError(
                f"Unsupported upload method: {upload_info.method}"
            )

        _logger.debug(
            "Uploading %d bytes to presigned URL (method=%s)",
            len(image_data),
            upload_info.method,
        )
        try:
            if method == "PUT":
                response = await self._upload_client.put(
                    upload_info.url,
                    content=image_data,
                    headers=headers,
                )
            else:
                response = await self._upload_client.post(
                    upload_info.url,
                    content=image_data,
                    headers=headers,
                )
            response.raise_for_status()
            _logger.debug(
                "Upload completed with status %d", response.status_code
            )
        except UDSImageUploadError:
            raise
        except Exception as e:
            _logger.error("Failed to upload image: %s", e)
            raise UDSImageUploadError(f"Failed to upload image: {e}") from e
