from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

_origin_request_id: ContextVar[str | None] = ContextVar(
    "async_uds_api_origin_request_id", default=None
)


def set_origin_request_id(value: str | None) -> Token[str | None]:
    """Set the origin request id for the current context.

    The value is sent verbatim in the X-Origin-Request-Id header and is
    never validated. Pass the returned token to reset_origin_request_id
    to restore the previous value.
    """
    return _origin_request_id.set(value)


def get_origin_request_id() -> str | None:
    """Return the origin request id set for the current context."""
    return _origin_request_id.get()


def reset_origin_request_id(token: Token[str | None]) -> None:
    """Restore the value that was active before the matching set call."""
    _origin_request_id.reset(token)


@contextmanager
def use_origin_request_id(value: str | None) -> Iterator[str | None]:
    """Bind the origin request id for the duration of the block."""
    token = _origin_request_id.set(value)
    try:
        yield value
    finally:
        _origin_request_id.reset(token)
