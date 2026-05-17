"""A2A transcript adapter for C4 checks."""
from __future__ import annotations

from typing import Any

from reference.bindings.a2a_agent import A2aAgent

from .common import bad_process_contract, base_transcript, email_contract, exap_error, provider_for_scenario, summarize_event


def artifact_data(task: dict[str, Any]) -> dict[str, Any]:
    return task["artifacts"][0]["data"]


class A2aTranscriptAdapter:
    binding = "a2a"

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        kind = scenario["kind"]
        if kind == "email_priority":
            return self.email_priority(scenario)
        if kind == "error_mapping":
            return self.error_mapping(scenario)
        raise ValueError(kind)

    def email_priority(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        agent = A2aAgent(provider)
        contract = email_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "email-priority", "a2a", "wait")
        draft = agent.create_contract("notify me about urgent approval requests", "a2a-draft")
        create = agent.create_contract({"contract": contract, "idempotency_key": scenario["scenario_id"]}, "a2a-create")
        wait = agent.wait({"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S", "include": ["event"]}, "a2a-wait")
        transcript["requests"] = [draft, create, wait]
        transcript["draft_status"] = artifact_data(draft).get("status")
        transcript["contract_id"] = artifact_data(create).get("contract_id")
        transcript["return_reason"] = artifact_data(wait).get("return_reason")
        transcript["event"] = summarize_event(artifact_data(wait).get("event"))
        transcript["attention_id"] = transcript["event"].get("attention_id")
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def error_mapping(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        agent = A2aAgent(provider)
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "a2a", "error")
        missing = agent.wait({"contract_id": "act_missing", "until": ["attention"], "timeout": "PT1S"}, "a2a-missing")
        bad = agent.create_contract({"contract": bad_process_contract()}, "a2a-bad")
        transcript["requests"] = [missing, bad]
        transcript["errors"] = [exap_error({"error": artifact_data(missing)}), exap_error({"error": artifact_data(bad)})]
        return transcript
