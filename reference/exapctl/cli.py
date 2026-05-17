#!/usr/bin/env python3
"""Minimal exapctl facade for the reference provider."""
from __future__ import annotations

from typing import Any

from reference.exapd import ReferenceProviderAdapter


class ExapCtl:
    def __init__(self, provider: ReferenceProviderAdapter | None = None) -> None:
        self.provider = provider or ReferenceProviderAdapter()

    def discover(self) -> dict[str, Any]:
        return self.provider.lifecycle("exap.discover", {}, "exapctl-discover")

    def contract_create(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.provider.lifecycle("exap.contract.create", params, "exapctl-create")

    def wait(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.provider.lifecycle("exap.wait", params, "exapctl-wait")

    def status(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.provider.lifecycle("exap.status", params, "exapctl-status")

    def ack(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.provider.lifecycle("exap.attention.ack", params, "exapctl-ack")

    def contract_revoke(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.provider.lifecycle("exap.contract.revoke", params, "exapctl-revoke")
