"""Attention event fixture builder for the reference provider."""
from __future__ import annotations

from typing import Any

from .common import clone_json, load_json


class EvidenceBuilder:
    def __init__(self) -> None:
        self.gpu_event = load_json("examples/02-gpu-idle-attention-event.json")
        self.mail_event = load_json("examples/04-mail-attention-event.json")

    def for_contract(self, contract_id: str) -> dict[str, Any]:
        if "email" in contract_id:
            return clone_json(self.mail_event)
        return clone_json(self.gpu_event)

    def attention_index(self) -> dict[str, dict[str, Any]]:
        return {
            self.gpu_event["data"]["attention_id"]: clone_json(self.gpu_event),
            self.mail_event["data"]["attention_id"]: clone_json(self.mail_event),
        }
