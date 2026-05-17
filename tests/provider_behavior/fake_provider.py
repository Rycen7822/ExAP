#!/usr/bin/env python3
"""Smoke-grade fake Provider used by the ExAP C2 behavior suite."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import copy
import importlib.util

try:
    from .adapter import EXAP_VERSION, ROOT, clone_json, error_response, load_json, ok_response
except ImportError:  # Allows direct script-style imports during local debugging.
    from adapter import EXAP_VERSION, ROOT, clone_json, error_response, load_json, ok_response  # type: ignore


def _load_conformance_helpers() -> Any:
    spec = importlib.util.spec_from_file_location("exap_conformance_helpers", ROOT / "tests" / "conformance.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load tests/conformance.py helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONF = _load_conformance_helpers()


@dataclass
class ContractRecord:
    contract: dict[str, Any]
    status: str
    version: int = 1
    recent_events: list[dict[str, Any]] = field(default_factory=list)


class FakeProviderAdapter:
    """Small deterministic provider that exercises C2 behavior without external services."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.process_capability = load_json("examples/05-provider-capability-process.json")
        self.mail_capability = load_json("examples/06-provider-capability-mail.json")
        self.gpu_event = load_json("examples/02-gpu-idle-attention-event.json")
        self.mail_event = load_json("examples/04-mail-attention-event.json")
        self.contracts: dict[str, ContractRecord] = {}
        self.idempotency: dict[str, str] = {}
        self.attention: dict[str, dict[str, Any]] = {
            self.gpu_event["data"]["attention_id"]: clone_json(self.gpu_event),
            self.mail_event["data"]["attention_id"]: clone_json(self.mail_event),
        }
        self.audit: list[dict[str, Any]] = []
        self.transitions: list[dict[str, Any]] = []
        self.observations: list[dict[str, Any]] = [
            {
                "observation_id": "obs_gpu_util_001",
                "subject_ref": "exap://local/gpu/0",
                "signal": "gpu.util.percent",
                "value": 4.2,
                "observed_at": "2026-05-16T12:07:00+09:00",
                "source": "local-process-provider",
            },
            {
                "observation_id": "obs_mail_relationship_001",
                "subject_ref": "exap://personal/mailbox/primary",
                "signal": "mail.sender.relationship",
                "value": "frequent_collaborator",
                "observed_at": "2026-05-16T09:15:00+09:00",
                "source": "mail-provider",
            },
        ]

    def discover(self, params: dict[str, Any]) -> dict[str, Any]:
        capability = self._select_capability_for_discover(params)
        return {"capability": clone_json(capability)}

    def lifecycle(self, method: str, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        self.audit.append({"method": method, "params": clone_json(params), "request_id": request_id})
        handlers = {
            "exap.discover": self._handle_discover,
            "exap.contract.create": self._handle_create,
            "exap.contract.get": self._handle_get,
            "exap.contract.list": self._handle_list,
            "exap.contract.update": self._handle_update,
            "exap.contract.pause": self._handle_pause,
            "exap.contract.resume": self._handle_resume,
            "exap.contract.revoke": self._handle_revoke,
            "exap.wait": self._handle_wait,
            "exap.stream.open": self._handle_stream_open,
            "exap.attention.ack": self._handle_ack,
            "exap.status": self._handle_status,
            "exap.observation.query": self._handle_observation_query,
        }
        handler = handlers.get(method)
        if handler is None:
            return error_response(request_id, -32601, "ExAP-4000", f"Unsupported method {method}", field="method")
        return handler(params, request_id)

    def open_stream(self, params: dict[str, Any]) -> dict[str, Any]:
        response = self.lifecycle("exap.stream.open", params, "stream-open")
        if "error" in response:
            return {"metadata": None, "frames": [{"type": "error", "error": response["error"]}]}
        contract_id = params["contract_id"]
        event = self._event_for_contract(contract_id)
        return {
            "metadata": response["result"],
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

    def push_fixture(self, contract: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
        return {
            "contract_id": contract["contract_id"],
            "attention_id": event["data"]["attention_id"],
            "transport": contract.get("delivery", {}).get("transports", [{}])[0].get("transport", "http_webhook"),
            "mode": "push",
            "attempt": 1,
            "success": True,
        }

    def snapshot_state(self, contract_id: str) -> dict[str, Any]:
        record = self.contracts.get(contract_id)
        if not record:
            return {"contract_id": contract_id, "status": "missing"}
        return {
            "contract_id": contract_id,
            "status": record.status,
            "version": str(record.version),
            "recent_events": [event["data"]["attention_id"] for event in record.recent_events],
        }

    def collect_audit(self) -> dict[str, Any]:
        return {"requests": clone_json(self.audit), "state_transitions": clone_json(self.transitions)}

    def _handle_discover(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        return ok_response(request_id, self.discover(params))

    def _handle_create(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        contract = clone_json(params["contract"])
        errors = self._contract_errors(contract)
        if errors:
            return error_response(request_id, -32602, "ExAP-4006", "Contract is not compatible with provider capability", field="params.contract", retryable=False)
        contract_id = contract.get("contract_id", f"act_fake_{len(self.contracts) + 1:03d}")
        contract["contract_id"] = contract_id
        idempotency_key = params.get("idempotency_key")
        if idempotency_key and idempotency_key in self.idempotency:
            contract_id = self.idempotency[idempotency_key]
            record = self.contracts[contract_id]
            return ok_response(request_id, {"contract_id": contract_id, "status": record.status, "effective_contract": clone_json(record.contract), "warnings": []})
        if params.get("validate_only"):
            return ok_response(request_id, {"contract_id": contract_id, "status": "draft", "effective_contract": contract, "warnings": []})
        self.contracts[contract_id] = ContractRecord(contract=contract, status="active")
        if idempotency_key:
            self.idempotency[idempotency_key] = contract_id
        self._transition(contract_id, None, "active", "create")
        return ok_response(request_id, {"contract_id": contract_id, "status": "active", "effective_contract": contract, "warnings": []})

    def _handle_get(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        result: dict[str, Any] = {"contract": clone_json(record.contract)}
        if params.get("include_state"):
            result["state"] = self.snapshot_state(params["contract_id"])
        return ok_response(request_id, result)

    def _handle_list(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        statuses = set(params.get("status", []))
        contracts = [clone_json(record.contract) for record in self.contracts.values() if not statuses or record.status in statuses]
        limit = params.get("limit")
        if limit:
            contracts = contracts[:limit]
        return ok_response(request_id, {"contracts": contracts})

    def _handle_update(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        expected = params.get("expected_version")
        if expected is not None and expected != str(record.version):
            return error_response(request_id, -32009, "ExAP-4090", "Contract version conflict", field="params.expected_version", retryable=True)
        patch = params.get("patch", {})
        if "lifecycle" in patch and isinstance(patch["lifecycle"], dict):
            record.contract.setdefault("lifecycle", {}).update(patch["lifecycle"])
        if "intent" in patch:
            record.contract["intent"] = patch["intent"]
        record.version += 1
        return ok_response(request_id, {"contract_id": params["contract_id"], "status": record.status, "effective_contract": clone_json(record.contract), "warnings": []})

    def _handle_pause(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        self._set_status(params["contract_id"], record, "paused", "pause")
        return ok_response(request_id, {"contract_id": params["contract_id"], "status": "paused"})

    def _handle_resume(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        self._set_status(params["contract_id"], record, "active", "resume")
        return ok_response(request_id, {"contract_id": params["contract_id"], "status": "active"})

    def _handle_revoke(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        self._set_status(params["contract_id"], record, "revoked", "revoke")
        return ok_response(request_id, {"contract_id": params["contract_id"], "status": "revoked"})

    def _handle_wait(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        until = params.get("until", [])
        if "timeout" in until:
            return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "timeout", "status": record.status, "state": self.snapshot_state(params["contract_id"])})
        if "interrupted" in until:
            return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "interrupted", "status": record.status, "state": self.snapshot_state(params["contract_id"])})
        event = self._event_for_contract(params["contract_id"])
        record.recent_events.append(clone_json(event))
        return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "attention", "status": record.status, "event": clone_json(event), "cursor": "cursor_event_001"})

    def _handle_stream_open(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        return ok_response(request_id, {"contract_id": params["contract_id"], "stream_id": f"stream_{params['contract_id']}", "status": record.status, "cursor": params.get("cursor", "cursor_start")})

    def _handle_ack(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        attention_id = params["attention_id"]
        if attention_id not in self.attention:
            return error_response(request_id, -32004, "ExAP-4040", "Attention event not found", field="params.attention_id", retryable=False)
        action = params["action"]
        status = {"seen": "acknowledged", "snooze": "snoozed", "dismiss": "dismissed", "escalate": "escalated"}[action]
        return ok_response(request_id, {"attention_id": attention_id, "action": action, "status": status})

    def _handle_status(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        result: dict[str, Any] = {"contract_id": params["contract_id"], "status": record.status}
        include = set(params.get("include", []))
        if "state" in include:
            result["state"] = self.snapshot_state(params["contract_id"])
        if "recent_events" in include:
            result["recent_events"] = clone_json(record.recent_events)
        if "metrics" in include:
            result["metrics"] = {"waiters": 0, "events_delivered": len(record.recent_events)}
        return ok_response(request_id, result)

    def _handle_observation_query(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        if "contract_id" in params and params["contract_id"] not in self.contracts:
            return error_response(request_id, -32004, "ExAP-4040", "Contract not found", field="params.contract_id", retryable=False)
        items = []
        for item in self.observations:
            if params.get("subject_ref") and item["subject_ref"] != params["subject_ref"]:
                continue
            if params.get("signal") and item["signal"] != params["signal"]:
                continue
            items.append(clone_json(item))
        return ok_response(request_id, {"items": items[: params.get("limit", len(items))]})

    def _select_capability_for_discover(self, params: dict[str, Any]) -> dict[str, Any]:
        requested_subjects = set(params.get("subject_types", []))
        requested_profiles = set(params.get("profile_ids", []))
        if requested_subjects & {"mailbox", "email_thread"} or "profile:email-priority" in requested_profiles:
            return self.mail_capability
        return self.process_capability

    def _capability_for_contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        subject_types = {subject.get("type") for subject in contract.get("scope", {}).get("subjects", [])}
        if subject_types & {"mailbox", "email_thread"}:
            return self.mail_capability
        return self.process_capability

    def _contract_errors(self, contract: dict[str, Any]) -> list[str]:
        capability = self._capability_for_contract(contract)
        errors = CONF.semantic_contract(contract)
        errors.extend(CONF.capability_compatibility_errors(contract, capability))
        return errors

    def _record_or_error(self, contract_id: str, request_id: str | int) -> ContractRecord | dict[str, Any]:
        record = self.contracts.get(contract_id)
        if record is None:
            return error_response(request_id, -32004, "ExAP-4040", "Contract not found", field="params.contract_id", retryable=False)
        return record

    def _set_status(self, contract_id: str, record: ContractRecord, status: str, action: str) -> None:
        old = record.status
        record.status = status
        record.version += 1
        record.contract.setdefault("lifecycle", {})["status"] = status
        self._transition(contract_id, old, status, action)

    def _transition(self, contract_id: str, old_status: str | None, new_status: str, action: str) -> None:
        self.transitions.append({"contract_id": contract_id, "from": old_status, "to": new_status, "action": action})

    def _event_for_contract(self, contract_id: str) -> dict[str, Any]:
        if "email" in contract_id:
            return self.mail_event
        return self.gpu_event
