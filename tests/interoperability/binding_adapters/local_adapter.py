"""Local JSON-RPC transcript adapter for C4 checks."""
from __future__ import annotations

from typing import Any

from .common import base_transcript, exap_error, exap_result, process_contract, provider_for_scenario, summarize_event


class LocalTranscriptAdapter:
    binding = "local"

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        contract = process_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "local_stdio", "wait")
        create = provider.lifecycle("exap.contract.create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "local-create")
        wait = provider.lifecycle("exap.wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S", "include": ["event"]}, "local-wait")
        ack = provider.lifecycle("exap.attention.ack", {"attention_id": "attn_gpu_idle_001", "action": "seen"}, "local-ack")
        transcript["requests"] = [create, wait, ack]
        transcript["contract_id"] = exap_result(create).get("contract_id")
        transcript["return_reason"] = exap_result(wait).get("return_reason")
        transcript["event"] = summarize_event(exap_result(wait).get("event"))
        transcript["attention_id"] = transcript["event"].get("attention_id")
        transcript["ack_status"] = exap_result(ack).get("status")
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        transcript["errors"] = [exap_error(wait)] if "error" in wait else []
        return transcript
