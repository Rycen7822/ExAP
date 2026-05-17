"""Smoke-grade A2A facade for the ExAP reference provider."""
from __future__ import annotations

from typing import Any

from reference.exapd import ReferenceProviderAdapter
from reference.exapd.common import clone_json, load_json


class A2aAgent:
    def __init__(self, provider: ReferenceProviderAdapter) -> None:
        self.provider = provider
        self.agent_card = load_json("examples/09-a2a-agent-card.json")

    def card(self) -> dict[str, Any]:
        return clone_json(self.agent_card)

    def create_contract(self, payload: dict[str, Any] | str, request_id: str) -> dict[str, Any]:
        if isinstance(payload, str):
            draft = load_json("examples/03-email-important-contract.json")
            draft["intent"] = payload
            result = {"contract_id": draft["contract_id"], "status": "draft", "effective_contract": draft, "warnings": [{"code": "validate_only_draft", "message": "Text input returns a draft for confirmation."}]}
            return self._task("create_attention_contract", "completed", result, "application/exap+json")
        response = self.provider.lifecycle("exap.contract.create", payload, request_id)
        return self._task("create_attention_contract", "completed" if "result" in response else "failed", response.get("result", response.get("error", {})), "application/exap+json")

    def wait(self, params: dict[str, Any], request_id: str) -> dict[str, Any]:
        response = self.provider.lifecycle("exap.wait", params, request_id)
        return self._task("wait_for_attention", "completed" if "result" in response else "failed", response.get("result", response.get("error", {})), "application/exap+json")

    def ack(self, params: dict[str, Any], request_id: str) -> dict[str, Any]:
        response = self.provider.lifecycle("exap.attention.ack", params, request_id)
        return self._task("ack_attention_event", "completed" if "result" in response else "failed", response.get("result", response.get("error", {})), "application/exap+json")

    def revoke(self, params: dict[str, Any], request_id: str) -> dict[str, Any]:
        response = self.provider.lifecycle("exap.contract.revoke", params, request_id)
        return self._task("revoke_attention_contract", "completed" if "result" in response else "failed", response.get("result", response.get("error", {})), "application/exap+json")

    def _task(self, skill: str, state: str, artifact: dict[str, Any], media_type: str) -> dict[str, Any]:
        return {"skill": skill, "state": state, "artifacts": [{"mediaType": media_type, "data": artifact}]}
