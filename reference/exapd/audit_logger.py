"""Audit records for reference smoke runs."""
from __future__ import annotations

from typing import Any

from .common import clone_json


class AuditLogger:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []

    def record(self, method: str, params: dict[str, Any], request_id: str | int) -> None:
        self.requests.append({"method": method, "params": clone_json(params), "request_id": request_id})

    def snapshot(self, transitions: list[dict[str, Any]]) -> dict[str, Any]:
        return {"requests": clone_json(self.requests), "state_transitions": clone_json(transitions)}
