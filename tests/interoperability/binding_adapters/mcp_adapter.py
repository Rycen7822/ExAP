"""MCP transcript adapter for C4 checks."""
from __future__ import annotations

from typing import Any

from reference.bindings.mcp_server import McpBinding

from .common import bad_process_contract, base_transcript, exap_error, exap_result, process_contract, provider_for_scenario, summarize_event


class McpTranscriptAdapter:
    binding = "mcp"

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        kind = scenario["kind"]
        if kind == "process_wait":
            return self.process_wait(scenario)
        if kind == "stream_push_recovery":
            return self.stream_push_recovery(scenario)
        if kind == "error_mapping":
            return self.error_mapping(scenario)
        raise ValueError(kind)

    def process_wait(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        mcp = McpBinding(provider)
        contract = process_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "mcp", "wait")
        create = mcp.call_tool("exap_contract_create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "mcp-create")
        wait = mcp.call_tool("exap_wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S", "include": ["event", "state"]}, "mcp-wait")
        status = mcp.call_tool("exap_status", {"contract_id": contract["contract_id"], "include": ["state", "metrics", "recent_events"]}, "mcp-status")
        ack = mcp.call_tool("exap_attention_ack", {"attention_id": "attn_gpu_idle_001", "action": "seen"}, "mcp-ack")
        transcript["requests"] = [create, wait, status, ack]
        transcript["contract_id"] = exap_result(create["content"]).get("contract_id")
        transcript["return_reason"] = exap_result(wait["content"]).get("return_reason")
        transcript["status"] = exap_result(status["content"]).get("status")
        transcript["event"] = summarize_event(exap_result(wait["content"]).get("event"))
        transcript["attention_id"] = transcript["event"].get("attention_id")
        transcript["ack_status"] = exap_result(ack["content"]).get("status")
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def stream_push_recovery(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        mcp = McpBinding(provider)
        contract = process_contract()
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "mcp", "stream")
        create = mcp.call_tool("exap_contract_create", {"contract": contract, "idempotency_key": scenario["scenario_id"]}, "mcp-create")
        stream = provider.open_stream({"contract_id": contract["contract_id"], "include": ["event"], "cursor": "cursor_start"})
        event_frame = next(frame for frame in stream["frames"] if frame["type"] == "event")
        progress = {"type": "progress", "cursor": "cursor_keepalive_001"}
        transcript["requests"] = [create, {"progress": progress}, {"stream": stream}]
        transcript["contract_id"] = exap_result(create["content"]).get("contract_id")
        transcript["stream_id"] = stream["metadata"]["stream_id"]
        transcript["frame_types"] = [frame["type"] for frame in stream["frames"]]
        transcript["attention_id"] = event_frame["event"]["data"]["attention_id"]
        transcript["event"] = summarize_event(event_frame["event"])
        transcript["push_success"] = True
        transcript["state_transitions"] = provider.collect_audit()["state_transitions"]
        return transcript

    def error_mapping(self, scenario: dict[str, Any]) -> dict[str, Any]:
        provider = provider_for_scenario()
        mcp = McpBinding(provider)
        transcript = base_transcript(self.binding, scenario["scenario_id"], "deep-learning-training", "mcp", "error")
        missing = mcp.call_tool("exap_status", {"contract_id": "act_missing"}, "mcp-missing")
        bad = mcp.call_tool("exap_contract_create", {"contract": bad_process_contract()}, "mcp-bad")
        transcript["requests"] = [missing, bad]
        transcript["errors"] = [exap_error(missing["content"]), exap_error(bad["content"])]
        return transcript
