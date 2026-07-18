from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from typing import Any, Protocol
from urllib.parse import urlsplit

SENSITIVE_PARAMS = frozenset({"phone", "uid", "code"})

_MASK = "***"
_VISIBLE_TAIL = 4
_DEFAULT_PORTS = {"http": 80, "https": 443}


def mask_value(value: object) -> str:
    text = str(value)
    if len(text) <= _VISIBLE_TAIL:
        return _MASK
    return f"{_MASK}{text[-_VISIBLE_TAIL:]}"


def mask_url(url: str) -> str:
    """Reduce an http(s) URL to scheme and host, dropping everything else.

    Userinfo, path, query and fragment are discarded outright: any of them
    may carry a credential or a signature. A non-default port is kept.
    Anything that is not an http(s) URL (a filesystem path, for example)
    is returned unchanged. A malformed http(s) URL never round-trips: its
    host is replaced by the mask rather than passed through.
    """
    try:
        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
    except Exception:
        return _MASK
    if scheme not in ("http", "https"):
        return url
    try:
        host = parsed.hostname
        port = parsed.port
    except Exception:
        return f"{scheme}://{_MASK}"
    if not host:
        return f"{scheme}://{_MASK}"
    if ":" in host:
        host = f"[{host}]"
    if port is not None and port != _DEFAULT_PORTS[scheme]:
        host = f"{host}:{port}"
    return f"{scheme}://{host}/{_MASK}"


def mask_params(
    params: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if params is None:
        return None
    return {
        key: mask_value(value) if key in SENSITIVE_PARAMS else value
        for key, value in params.items()
    }


_TEMPLATES: dict[str, str] = {
    "uds.request": (
        "%(method)s %(path)s%(params)s "
        "[X-Origin-Request-Id=%(request_id)s] [X-Timestamp=%(timestamp)s]"
    ),
    "uds.response": "%(method)s %(path)s -> %(status)d OK in %(elapsed).3fs",
    "uds.error": (
        "%(method)s %(path)s -> %(status)d Error in "
        "%(elapsed).3fs%(error_code)s"
    ),
    "uds.retry": "Retry attempt %(attempt)d for %(method)s %(path)s",
    "uds.image.upload_url_request": (
        "Requesting upload URL for content_type=%(content_type)s"
    ),
    "uds.image.upload_url_received": "Got upload URL: image_id=%(image_id)s",
    "uds.image.upload_start_bytes": (
        "Uploading %(size)d bytes with content_type=%(content_type)s"
    ),
    "uds.image.upload_start_source": (
        "Uploading from %(source)s with content_type=%(content_type)s"
    ),
    "uds.image.read": "Read %(size)d bytes",
    "uds.image.uploaded": (
        "Image uploaded successfully: image_id=%(image_id)s"
    ),
    "uds.image.file_read_start": "Reading image from file: %(path)s",
    "uds.image.file_read_done": "Read %(size)d bytes from %(path)s",
    "uds.image.file_not_found": "File not found: %(path)s",
    "uds.image.file_read_failed": "Failed to read file %(path)s: %(error)s",
    "uds.image.download_start": "Downloading image from URL: %(url)s",
    "uds.image.download_done": "Downloaded %(size)d bytes from %(url)s",
    "uds.image.download_failed": (
        "Failed to download image from %(url)s: %(error)s"
    ),
    "uds.image.presigned_upload_start": (
        "Uploading %(size)d bytes to presigned URL (method=%(method)s)"
    ),
    "uds.image.presigned_upload_done": (
        "Upload completed with status %(status)d"
    ),
    "uds.image.upload_failed": "Failed to upload image: %(error)s",
}


class LoggerProtocol(Protocol):
    def debug(self, event: str, **fields: Any) -> None: ...

    def info(self, event: str, **fields: Any) -> None: ...

    def warning(self, event: str, **fields: Any) -> None: ...

    def error(self, event: str, **fields: Any) -> None: ...


def _render_params(params: Mapping[str, Any] | None) -> str:
    if not params:
        return ""
    body = " ".join(f"{key}={value}" for key, value in params.items())
    return f" [{body}]"


def _render_error_code(error_code: object) -> str:
    if not error_code:
        return ""
    return f" [errorCode={error_code}]"


def _safe_text(value: object) -> str:
    """Stringify a field value, tolerating a broken ``__str__``."""
    try:
        return str(value)
    except Exception:
        return "<unprintable>"


def _render_fallback(event: str, fields: Mapping[str, Any]) -> str:
    body = "".join(
        f" {key}={_safe_text(value)}" for key, value in fields.items()
    )
    return f"{event}{body}"


def _render(event: str, fields: Mapping[str, Any]) -> str:
    template = _TEMPLATES.get(event)
    if template is None:
        return _render_fallback(event, fields)

    try:
        presentation = dict(fields)
        if "params" in presentation:
            presentation["params"] = _render_params(fields["params"])
        if "error_code" in presentation:
            presentation["error_code"] = _render_error_code(
                fields["error_code"]
            )
        return template % presentation
    except Exception:
        return _render_fallback(event, fields)


class StdlibLoggerAdapter:
    """Render structured events into the library's classic log format."""

    def __init__(
        self, logger: logging.Logger | logging.LoggerAdapter[Any]
    ) -> None:
        self._logger = logger

    def debug(self, event: str, **fields: Any) -> None:
        self._log(logging.DEBUG, event, fields)

    def info(self, event: str, **fields: Any) -> None:
        self._log(logging.INFO, event, fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._log(logging.WARNING, event, fields)

    def error(self, event: str, **fields: Any) -> None:
        self._log(logging.ERROR, event, fields)

    def _log(self, level: int, event: str, fields: Mapping[str, Any]) -> None:
        try:
            if not self._logger.isEnabledFor(level):
                return
            self._logger.log(
                level, _render(event, fields), extra={"uds": dict(fields)}
            )
        except Exception:
            if os.environ.get("ASYNC_UDS_API_DEBUG_LOGGING"):
                raise
