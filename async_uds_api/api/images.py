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


def _describe_exception(exc: BaseException) -> str:
    """Summarise a third-party exception without quoting its text."""
    name = type(exc).__name__
    if isinstance(exc, httpx.HTTPStatusError):
        return f"{name} (status {exc.response.status_code})"
    return name


def _mask_source(source: str | Path) -> str:
    """Mask the query string of http(s) sources, leaving paths untouched."""
    text = str(source)
    if urlparse(text).scheme in ("http", "https"):
        return mask_url(text)
    return text


def _scrub_http_exception(exc: BaseException, method: str, url: str) -> None:
    """Replace an httpx exception's own text with a safe summary.

    The exception object stays intact as ``__cause__`` so its type and
    ``.response`` remain inspectable, but a formatted traceback no longer
    carries the presigned URL's query string.
    """
    if not isinstance(exc, (httpx.HTTPError, httpx.InvalidURL)):
        return
    if isinstance(exc, httpx.HTTPStatusError):
        head = str(exc.response.status_code)
    else:
        head = type(exc).__name__
    exc.args = (f"{head} for {method} {mask_url(url)}",)


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
                source=_mask_source(source),
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
                f"Cannot detect content type for '{_mask_source(source_str)}'."
                " Provide content_type explicitly."
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
            detail = _describe_exception(e)
            self._logger.error(
                "uds.image.file_read_failed", path=path, error=detail
            )
            raise UDSImageReadError(
                f"Failed to read file {path}: {detail}"
            ) from e

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
            detail = _describe_exception(e)
            self._logger.error(
                "uds.image.download_failed",
                url=masked_url,
                error=detail,
            )
            _scrub_http_exception(e, "GET", url)
            raise UDSImageDownloadError(
                f"Failed to download image from {masked_url}: {detail}"
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
            detail = f"{mask_url(upload_info.url)}: {_describe_exception(e)}"
            self._logger.error("uds.image.upload_failed", error=detail)
            _scrub_http_exception(e, method, upload_info.url)
            raise UDSImageUploadError(
                f"Failed to upload image: {detail}"
            ) from e
