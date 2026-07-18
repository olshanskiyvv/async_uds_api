from __future__ import annotations

from collections.abc import Mapping
from typing import Any

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
