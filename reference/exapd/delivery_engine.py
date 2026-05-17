"""Delivery helpers for wait, stream, and push smoke paths."""
from __future__ import annotations

from typing import Any

from .common import clone_json


class DeliveryEngine:
    def stream_frames(self, metadata: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
        return {
            "metadata": clone_json(metadata),
            "frames": [
                {"type": "keepalive", "cursor": "cursor_keepalive_001"},
                {"type": "event", "event": clone_json(event), "cursor": "cursor_event_001"},
                {
                    "type": "error",
                    "error": {"code": -32000, "message": "diagnostic frame", "data": {"exap_code": "ExAP-5000", "retryable": True}},
                    "cursor": "cursor_error_001",
                },
            ],
        }

    def push_report(self, contract: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
        return {
            "contract_id": contract["contract_id"],
            "attention_id": event["data"]["attention_id"],
            "transport": contract.get("delivery", {}).get("transports", [{}])[0].get("transport", "http_webhook"),
            "mode": "push",
            "attempt": 1,
            "success": True,
        }
