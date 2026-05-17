"""Shared helpers for C4 binding adapters."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import json

from reference.exapd import ReferenceProviderAdapter
from reference.exapd.common import load_json

ROOT = Path(__file__).resolve().parents[3]


def clone(value: Any) -> Any:
    return copy.deepcopy(value)


def process_contract() -> dict[str, Any]:
    return load_json("examples/01-process-wait-contract.json")


def email_contract() -> dict[str, Any]:
    return load_json("examples/03-email-important-contract.json")


def bad_process_contract() -> dict[str, Any]:
    contract = process_contract()
    contract["contract_id"] = "act_bad_signal_001"
    contract.setdefault("scope", {}).setdefault("signals", []).append("made.up.signal")
    first = contract["rules"][0]["condition"]
    first["type"] = "signal"
    first.pop("event_type", None)
    first["signal"] = "made.up.signal"
    first["operator"] = "eq"
    first["value"] = 1
    return contract


def exap_result(envelope: dict[str, Any]) -> dict[str, Any]:
    return envelope.get("result", {})


def exap_error(envelope: dict[str, Any]) -> dict[str, Any]:
    error = envelope.get("error", {})
    data = error.get("data", {})
    return {"code": error.get("code"), "exap_code": data.get("exap_code"), "field": data.get("field"), "retryable": data.get("retryable")}


def summarize_event(event: dict[str, Any] | None) -> dict[str, Any]:
    if not event:
        return {}
    data = event.get("data", {})
    return {
        "attention_id": data.get("attention_id"),
        "type": event.get("type"),
        "status": data.get("status"),
        "rule_id": data.get("rule", {}).get("rule_id"),
        "payload_keys": sorted(data.get("payload", {}).keys()),
        "evidence_count": len(data.get("evidence", [])),
    }


def base_transcript(binding: str, scenario_id: str, profile: str, transport: str, delivery_mode: str) -> dict[str, Any]:
    return {
        "binding": binding,
        "scenario_id": scenario_id,
        "version": "0.2.0-draft",
        "profile": profile,
        "transport": transport,
        "delivery_mode": delivery_mode,
        "content_mode": "structured",
        "requests": [],
        "state_transitions": [],
        "errors": [],
    }


def provider_for_scenario() -> ReferenceProviderAdapter:
    return ReferenceProviderAdapter()
