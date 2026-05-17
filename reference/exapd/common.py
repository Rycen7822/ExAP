"""Small file/JSON helpers for the ExAP reference implementation."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import json

ROOT = Path(__file__).resolve().parents[2]
EXAP_VERSION = "0.2.0-draft"


def load_json(relative_path: str | Path) -> Any:
    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def clone_json(value: Any) -> Any:
    return copy.deepcopy(value)


def ok_response(request_id: str | int, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(
    request_id: str | int,
    code: int,
    exap_code: str,
    message: str,
    *,
    field: str | None = None,
    retryable: bool = False,
) -> dict[str, Any]:
    data: dict[str, Any] = {"exap_code": exap_code, "retryable": retryable}
    if field:
        data["field"] = field
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message, "data": data}}
