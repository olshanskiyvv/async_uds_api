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
from async_uds_api.log import mask_url
from async_uds_api.models import ImageUploadUrl

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient

_MIME_RE = re.compile(
    r"^[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+/[a-zA-Z0-9!#$%^&\*\_\-+{}|\.]+$"
)


class ImagesAPI:
    def __init__(self, client: "UDSClient", timeout: float) -> None:
        self._client = client
        self._timeout = timeout
        self._logger = client._logger
        self._upload_client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        """Close the underlying HTTP client used for presigned-URL uploads."""
        await self._upload_client.aclose()

    async def get_upload_url(self, content_type: str) -> ImageUploadUrl:
        """Request a presigned upload URL for the given MIME type."""
        self._validate_content_type(content_type)
        self._logger.debug(
            "uds.image.upload_url_request", content_type=content_type
        )
        body = {"contentType": content_type}
        data = await self._client._post_json("/image-upload-url", body=body)
        result = ImageUploadUrl.model_validate(data)
        self._logger.info(
            "uds.image.upload_url_received", image_id=result.image_id
        )
        return result

    async def upload(
        self,
        source: str | Path | bytes,
        content_type: str | None = None,
    ) -> str:
        """Upload an image from a path, URL, or bytes; return the image ID."""
        if isinstance(source, bytes):
            if content_type is None:
                raise UDSImageUnsupportedSourceError(
                    "content_type is required when source is bytes"
                )
            self._validate_content_type(content_type)
            self._logger.debug(
                "uds.image.upload_start_bytes",
                size=len(source),
                content_type=content_type,
            )
        else:
            if content_type is not None:
                self._validate_content_type(content_type)
            else:
                content_type = self._detect_content_type(source)
            self._logger.debug(
                "uds.image.upload_start_source",
                source=source,
                content_type=content_type,
            )

        image_data = await self._read_image_data(source)
        self._logger.debug("uds.image.read", size=len(image_data))

        upload_info = await self.get_upload_url(content_type)
        await self._upload_to_url(upload_info, image_data)

        self._logger.info("uds.image.uploaded", image_id=upload_info.image_id)
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
        self._logger.debug("uds.image.file_read_start", path=path)
        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
            self._logger.debug(
                "uds.image.file_read_done", size=len(data), path=path
            )
            return data
        except FileNotFoundError:
            self._logger.error("uds.image.file_not_found", path=path)
            raise UDSImageReadError(f"File not found: {path}")
        except Exception as e:
            self._logger.error(
                "uds.image.file_read_failed", path=path, error=e
            )
            raise UDSImageReadError(f"Failed to read file {path}: {e}") from e

    async def _download_from_url(self, url: str) -> bytes:
        masked_url = mask_url(url)
        self._logger.debug("uds.image.download_start", url=masked_url)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
            self._logger.debug(
                "uds.image.download_done",
                size=len(response.content),
                url=masked_url,
            )
            return response.content
        except Exception as e:
            error_text = str(e).replace(url, masked_url)
            self._logger.error(
                "uds.image.download_failed",
                url=masked_url,
                error=error_text,
            )
            raise UDSImageDownloadError(
                f"Failed to download image from {masked_url}: {error_text}"
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

        self._logger.debug(
            "uds.image.presigned_upload_start",
            size=len(image_data),
            method=upload_info.method,
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
            self._logger.debug(
                "uds.image.presigned_upload_done",
                status=response.status_code,
            )
        except UDSImageUploadError:
            raise
        except Exception as e:
            self._logger.error("uds.image.upload_failed", error=e)
            raise UDSImageUploadError(f"Failed to upload image: {e}") from e
