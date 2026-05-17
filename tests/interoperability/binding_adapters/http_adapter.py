"""HTTP transcript adapter for C4 checks."""
from __future__ import annotations

from typing import Any

from reference.bindings.http_server import HttpBinding

from .common import bad_process_contract, base_transcript, email_contract, exap_error, exap_result, process_contract, provider_for_scenario, summarize_event


class HttpTranscriptAdapter:
    binding = "http"

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        kind = scenario["kind"]
        if kind == "process_wait":
            return self.process_wait(scenario)
        if kind == "email_priority":
            return self.email_priority(scenario)
        if kind == "stream_push_recovery":
            return self.stream_push_recovery(scenario)
        if kind == "error_mapping":
            return self.error_mapping(scenario)
        raise ValueError(kind)

    def process_wait(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        http = HttpBinding(provider)
        contract = process_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "http_webhook", "wait")
        create = http.post_jsonrpc("exap.contract.create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "http-create")
        wait = http.post_jsonrpc("exap.wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S", "include": ["event", "state"]}, "http-wait")
        status = http.post_jsonrpc("exap.status", {"contract_id": contract["contract_id"], "include": ["state", "metrics", "recent_events"]}, "http-status")
        ack = http.post_jsonrpc("exap.attention.ack", {"attention_id": "attn_gpu_idle_001", "action": "seen"}, "http-ack")
        transcript["requests"] = [create, wait, status, ack]
        transcript["contract_id"] = exap_result(create["body"]).get("contract_id")
        transcript["return_reason"] = exap_result(wait["body"]).get("return_reason")
        transcript["status"] = exap_result(status["body"]).get("status")
        transcript["event"] = summarize_event(exap_result(wait["body"]).get("event"))
        transcript["attention_id"] = transcript["event"].get("attention_id")
        transcript["ack_status"] = exap_result(ack["body"]).get("status")
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def email_priority(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        http = HttpBinding(provider)
        contract = email_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "email-priority", "http_webhook", "wait")
        draft = http.post_jsonrpc("exap.contract.create", {"contract": contract, "validate_only": True}, "http-draft")
        create = http.post_jsonrpc("exap.contract.create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "http-create")
        wait = http.post_jsonrpc("exap.wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S", "include": ["event"]}, "http-wait")
        transcript["requests"] = [draft, create, wait]
        transcript["draft_status"] = exap_result(draft["body"]).get("status")
        transcript["contract_id"] = exap_result(create["body"]).get("contract_id")
        transcript["return_reason"] = exap_result(wait["body"]).get("return_reason")
        transcript["event"] = summarize_event(exap_result(wait["body"]).get("event"))
        transcript["attention_id"] = transcript["event"].get("attention_id")
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def stream_push_recovery(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        http = HttpBinding(provider)
        contract = process_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "sse", "stream")
        create = http.post_jsonrpc("exap.contract.create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "http-create")
        stream = provider.open_stream({"contract_id": contract["contract_id"], "include": ["event"], "cursor": "cursor_start"})
        event_frame = next(frame for frame in stream["frames"] if frame["type"] == "event")
        push = provider.push_fixture(contract, event_frame["event"])
        transcript["requests"] = [create, {"stream": stream}, {"push": push}]
        transcript["contract_id"] = exap_result(create["body"]).get("contract_id")
        transcript["stream_id"] = stream["metadata"]["stream_id"]
        transcript["frame_types"] = [frame["type"] for frame in stream["frames"]]
        transcript["attention_id"] = event_frame["event"]["data"]["attention_id"]
        transcript["event"] = summarize_event(event_frame["event"])
        transcript["push_success"] = push["success"]
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def error_mapping(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        http = HttpBinding(provider)
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "http_webhook", "error")
        missing = http.post_jsonrpc("exap.contract.get", {"contract_id": "act_missing"}, "http-missing")
        bad = http.post_jsonrpc("exap.contract.create", {"contract": bad_process_contract()}, "http-bad")
        transcript["requests"] = [missing, bad]
        transcript["errors"] = [exap_error(missing["body"]), exap_error(bad["body"])]
        return transcript
