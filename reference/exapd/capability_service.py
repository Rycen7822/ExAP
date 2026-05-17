"""Capability loading and filtering for the ExAP reference provider."""
from __future__ import annotations

from typing import Any

from .common import clone_json, load_json


class CapabilityService:
    def __init__(self) -> None:
        self.process_capability = load_json("examples/05-provider-capability-process.json")
        self.mail_capability = load_json("examples/06-provider-capability-mail.json")

    def discover(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"capability": clone_json(self.select(params))}

    def select(self, params: dict[str, Any]) -> dict[str, Any]:
        subject_types = set(params.get("subject_types", []))
        profile_ids = set(params.get("profile_ids", []))
        if subject_types & {"mailbox", "email_thread"} or "profile:email-priority" in profile_ids:
            return self.mail_capability
        return self.process_capability

    def for_contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        subject_types = {subject.get("type") for subject in contract.get("scope", {}).get("subjects", [])}
        if subject_types & {"mailbox", "email_thread"}:
            return self.mail_capability
        return self.process_capability
