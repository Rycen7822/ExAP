#!/usr/bin/env python3
"""Shared adapter types and helpers for ExAP C2 provider behavior checks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol
import copy
import json

ROOT = Path(__file__).resolve().parents[2]
EXAP_VERSION = "0.2.0-draft"


class ProviderAdapter(Protocol):
    """Black-box provider surface used by the C2 suite."""

    def discover(self, params: dict[str, Any]) -> dict[str, Any]:
        ...

    def lifecycle(self, method: str, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        ...

    def open_stream(self, params: dict[str, Any]) -> dict[str, Any]:
        ...

    def push_fixture(self, contract: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
        ...

    def snapshot_state(self, contract_id: str) -> dict[str, Any]:
        ...

    def collect_audit(self) -> dict[str, Any]:
        ...


def load_json(relative_path: str | Path) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as f:
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
