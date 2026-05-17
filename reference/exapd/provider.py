"""C2-compatible smoke-grade ExAP reference provider."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .audit_logger import AuditLogger
from .capability_service import CapabilityService
from .common import clone_json, error_response, load_json, ok_response
from .contract_store import ContractRecord, ContractStore
from .delivery_engine import DeliveryEngine
from .evidence_builder import EvidenceBuilder
from .fake_collectors import FakeCollectors
from .rule_engine import RuleEngine


class ReferenceProviderAdapter:
    """Reference provider target for C2/C3/C4 smoke suites."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.capabilities = CapabilityService()
        self.store = ContractStore()
        self.audit_log = AuditLogger()
        self.rules = RuleEngine()
        self.evidence = EvidenceBuilder()
        self.delivery = DeliveryEngine()
        self.collectors = FakeCollectors()
        self.attention = self.evidence.attention_index()
        self.contracts = self.store.contracts
        self.idempotency = self.store.idempotency
        self.audit = self.audit_log.requests
        self.transitions = self.store.transitions

    def discover(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.capabilities.discover(params)

    def lifecycle(self, method: str, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        self.audit_log.record(method, params, request_id)
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
        event = self.evidence.for_contract(params["contract_id"])
        return self.delivery.stream_frames(response["result"], event)

    def push_fixture(self, contract: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
        return self.delivery.push_report(contract, event)

    def snapshot_state(self, contract_id: str) -> dict[str, Any]:
        return self.store.snapshot(contract_id)

    def collect_audit(self) -> dict[str, Any]:
        return self.audit_log.snapshot(self.store.transitions)

    def healthz(self) -> dict[str, Any]:
        return {"status": "ok", "component": "exapd", "version": "0.2.0-draft"}

    def readyz(self) -> dict[str, Any]:
        return {"status": "ready", "capabilities_loaded": 2, "contracts": self.store.count()}

    def metrics(self) -> str:
        return "\n".join([
            "# HELP exap_contracts_total Number of contracts in memory.",
            "# TYPE exap_contracts_total gauge",
            f"exap_contracts_total {self.store.count()}",
            "# HELP exap_audit_records_total Number of lifecycle requests recorded.",
            "# TYPE exap_audit_records_total counter",
            f"exap_audit_records_total {len(self.audit_log.requests)}",
        ]) + "\n"

    def dlq(self) -> dict[str, Any]:
        return {"items": [], "count": 0}

    def _handle_discover(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        return ok_response(request_id, self.discover(params))

    def _handle_create(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        contract = clone_json(params["contract"])
        errors = self.rules.compatibility_errors(contract, self.capabilities.for_contract(contract))
        if errors:
            return error_response(request_id, -32602, "ExAP-4006", "Contract is not compatible with provider capability", field="params.contract")
        contract_id = contract.get("contract_id", f"act_reference_{self.store.count() + 1:03d}")
        contract["contract_id"] = contract_id
        idempotency_key = params.get("idempotency_key")
        if idempotency_key and idempotency_key in self.store.idempotency:
            record = self.store.contracts[self.store.idempotency[idempotency_key]]
            return ok_response(request_id, self._create_result(record, []))
        if params.get("validate_only"):
            return ok_response(request_id, {"contract_id": contract_id, "status": "draft", "effective_contract": contract, "warnings": []})
        record = self.store.create(contract, idempotency_key)
        return ok_response(request_id, self._create_result(record, []))

    def _handle_get(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        result: dict[str, Any] = {"contract": clone_json(record.contract)}
        if params.get("include_state"):
            result["state"] = self.store.snapshot(params["contract_id"])
        return ok_response(request_id, result)

    def _handle_list(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        contracts = self.store.active_contracts(set(params.get("status", [])))
        return ok_response(request_id, {"contracts": contracts[: params.get("limit", len(contracts))]})

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
        return ok_response(request_id, self._create_result(record, []))

    def _handle_pause(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        return self._transition_response(params, request_id, "paused", "pause")

    def _handle_resume(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        return self._transition_response(params, request_id, "active", "resume")

    def _handle_revoke(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        return self._transition_response(params, request_id, "revoked", "revoke")

    def _handle_wait(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        until = params.get("until", [])
        if "timeout" in until:
            return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "timeout", "status": record.status, "state": self.store.snapshot(params["contract_id"])})
        if "interrupted" in until:
            return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "interrupted", "status": record.status, "state": self.store.snapshot(params["contract_id"])})
        event = self.evidence.for_contract(params["contract_id"])
        record.recent_events.append(clone_json(event))
        return ok_response(request_id, {"contract_id": params["contract_id"], "return_reason": "attention", "status": record.status, "event": event, "cursor": "cursor_event_001"})

    def _handle_stream_open(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        return ok_response(request_id, {"contract_id": params["contract_id"], "stream_id": f"stream_{params['contract_id']}", "status": record.status, "cursor": params.get("cursor", "cursor_start")})

    def _handle_ack(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        if params["attention_id"] not in self.attention:
            return error_response(request_id, -32004, "ExAP-4040", "Attention event not found", field="params.attention_id")
        action = params["action"]
        status = {"seen": "acknowledged", "snooze": "snoozed", "dismiss": "dismissed", "escalate": "escalated"}[action]
        return ok_response(request_id, {"attention_id": params["attention_id"], "action": action, "status": status})

    def _handle_status(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        result: dict[str, Any] = {"contract_id": params["contract_id"], "status": record.status}
        include = set(params.get("include", []))
        if "state" in include:
            result["state"] = self.store.snapshot(params["contract_id"])
        if "recent_events" in include:
            result["recent_events"] = clone_json(record.recent_events)
        if "metrics" in include:
            result["metrics"] = {"waiters": 0, "events_delivered": len(record.recent_events)}
        return ok_response(request_id, result)

    def _handle_observation_query(self, params: dict[str, Any], request_id: str | int) -> dict[str, Any]:
        if "contract_id" in params and self.store.get(params["contract_id"]) is None:
            return error_response(request_id, -32004, "ExAP-4040", "Contract not found", field="params.contract_id")
        return ok_response(request_id, {"items": self.collectors.query(params)})

    def _record_or_error(self, contract_id: str, request_id: str | int) -> ContractRecord | dict[str, Any]:
        record = self.store.get(contract_id)
        if record is None:
            return error_response(request_id, -32004, "ExAP-4040", "Contract not found", field="params.contract_id")
        return record

    def _transition_response(self, params: dict[str, Any], request_id: str | int, status: str, action: str) -> dict[str, Any]:
        record = self._record_or_error(params["contract_id"], request_id)
        if isinstance(record, dict):
            return record
        self.store.set_status(params["contract_id"], record, status, action)
        return ok_response(request_id, {"contract_id": params["contract_id"], "status": status})

    def _create_result(self, record: ContractRecord, warnings: list[dict[str, Any]]) -> dict[str, Any]:
        return {"contract_id": record.contract["contract_id"], "status": record.status, "effective_contract": clone_json(record.contract), "warnings": warnings}


def load_process_contract() -> dict[str, Any]:
    return load_json("examples/01-process-wait-contract.json")


def load_email_contract() -> dict[str, Any]:
    return load_json("examples/03-email-important-contract.json")
