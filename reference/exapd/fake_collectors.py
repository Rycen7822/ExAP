"""Deterministic fake collector data for reference smoke runs."""
from __future__ import annotations

from typing import Any

from .common import clone_json


class FakeCollectors:
    def __init__(self) -> None:
        self.observations = [
            {
                "observation_id": "obs_gpu_util_001",
                "subject_ref": "exap://local/gpu/0",
                "signal": "gpu.util.percent",
                "value": 4.2,
                "observed_at": "2026-05-16T12:07:00+09:00",
                "source": "reference-process-provider",
            },
            {
                "observation_id": "obs_mail_relationship_001",
                "subject_ref": "exap://personal/mailbox/primary",
                "signal": "mail.sender.relationship",
                "value": "frequent_collaborator",
                "observed_at": "2026-05-16T09:15:00+09:00",
                "source": "reference-mail-provider",
            },
        ]

    def query(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        items = []
        for item in self.observations:
            if params.get("subject_ref") and item["subject_ref"] != params["subject_ref"]:
                continue
            if params.get("signal") and item["signal"] != params["signal"]:
                continue
            items.append(clone_json(item))
        return items[: params.get("limit", len(items))]
