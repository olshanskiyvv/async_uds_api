from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Protocol

SENSITIVE_PARAMS = frozenset({"phone", "uid", "code"})

_MASK = "***"
_VISIBLE_TAIL = 4


def mask_value(value: object) -> str:
    text = str(value)
    if len(text) <= _VISIBLE_TAIL:
        return _MASK
    return f"{_MASK}{text[-_VISIBLE_TAIL:]}"


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
        "%(method)s %(path)s -> %(status)d Error in %(elapsed).3fs: "
        "%(message)s%(error_code)s"
    ),
    "uds.retry": "Retry attempt %(attempt)d for %(method)s %(path)s",
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


def _render_fallback(event: str, fields: Mapping[str, Any]) -> str:
    body = "".join(f" {key}={value}" for key, value in fields.items())
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

    def __init__(self, logger: logging.Logger) -> None:
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
        if not self._logger.isEnabledFor(level):
            return
        try:
            self._logger.log(
                level, _render(event, fields), extra={"uds": dict(fields)}
            )
        except Exception:
            pass
