"""In-memory contract store for reference smoke runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import clone_json


@dataclass
class ContractRecord:
    contract: dict[str, Any]
    status: str
    version: int = 1
    recent_events: list[dict[str, Any]] = field(default_factory=list)


class ContractStore:
    def __init__(self) -> None:
        self.contracts: dict[str, ContractRecord] = {}
        self.idempotency: dict[str, str] = {}
        self.transitions: list[dict[str, Any]] = []

    def count(self) -> int:
        return len(self.contracts)

    def get(self, contract_id: str) -> ContractRecord | None:
        return self.contracts.get(contract_id)

    def active_contracts(self, statuses: set[str]) -> list[dict[str, Any]]:
        return [clone_json(record.contract) for record in self.contracts.values() if not statuses or record.status in statuses]

    def create(self, contract: dict[str, Any], idempotency_key: str | None) -> ContractRecord:
        contract_id = contract.get("contract_id", f"act_reference_{len(self.contracts) + 1:03d}")
        contract["contract_id"] = contract_id
        if idempotency_key and idempotency_key in self.idempotency:
            return self.contracts[self.idempotency[idempotency_key]]
        record = ContractRecord(contract=contract, status="active")
        self.contracts[contract_id] = record
        if idempotency_key:
            self.idempotency[idempotency_key] = contract_id
        self.transition(contract_id, None, "active", "create")
        return record

    def set_status(self, contract_id: str, record: ContractRecord, status: str, action: str) -> None:
        old = record.status
        record.status = status
        record.version += 1
        record.contract.setdefault("lifecycle", {})["status"] = status
        self.transition(contract_id, old, status, action)

    def transition(self, contract_id: str, old_status: str | None, new_status: str, action: str) -> None:
        self.transitions.append({"contract_id": contract_id, "from": old_status, "to": new_status, "action": action})

    def snapshot(self, contract_id: str) -> dict[str, Any]:
        record = self.get(contract_id)
        if record is None:
            return {"contract_id": contract_id, "status": "missing"}
        return {
            "contract_id": contract_id,
            "status": record.status,
            "version": str(record.version),
            "recent_events": [event["data"]["attention_id"] for event in record.recent_events],
        }
