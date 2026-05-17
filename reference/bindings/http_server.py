"""Smoke-grade HTTP binding facade for the ExAP reference provider."""
from __future__ import annotations

from typing import Any

from reference.exapd import ReferenceProviderAdapter


class HttpBinding:
    def __init__(self, provider: ReferenceProviderAdapter) -> None:
        self.provider = provider

    def post_jsonrpc(self, method: str, params: dict[str, Any], request_id: str) -> dict[str, Any]:
        response = self.provider.lifecycle(method, params, request_id)
        return {"status": 200 if "result" in response else self._status_for_error(response), "body": response, "headers": {"ExAP-Version": "0.2.0-draft", "X-Request-ID": request_id}}

    def healthz(self) -> dict[str, Any]:
        return {"status": 200, "body": self.provider.healthz()}

    def readyz(self) -> dict[str, Any]:
        return {"status": 200, "body": self.provider.readyz()}

    def metrics(self) -> dict[str, Any]:
        return {"status": 200, "body": self.provider.metrics(), "headers": {"Content-Type": "text/plain; version=0.0.4"}}

    def dlq(self) -> dict[str, Any]:
        return {"status": 200, "body": self.provider.dlq()}

    def _status_for_error(self, response: dict[str, Any]) -> int:
        code = response.get("error", {}).get("code")
        if code == -32602:
            return 400
        if code == -32004:
            return 404
        if code == -32009:
            return 409
        return 500
