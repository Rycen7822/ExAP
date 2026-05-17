"""Smoke-grade MCP binding facade for the ExAP reference provider."""
from __future__ import annotations

from typing import Any

from reference.exapd import ReferenceProviderAdapter
from reference.exapd.common import load_json


TOOL_TO_METHOD = {
    "exap_discover": "exap.discover",
    "exap_contract_create": "exap.contract.create",
    "exap_wait": "exap.wait",
    "exap_status": "exap.status",
    "exap_attention_ack": "exap.attention.ack",
    "exap_contract_revoke": "exap.contract.revoke",
}


class McpBinding:
    def __init__(self, provider: ReferenceProviderAdapter) -> None:
        self.provider = provider
        self.manifest = load_json("examples/08-mcp-tools.json")

    def list_tools(self) -> list[str]:
        return [tool["name"] for tool in self.manifest["tools"]]

    def call_tool(self, name: str, arguments: dict[str, Any], request_id: str) -> dict[str, Any]:
        method = TOOL_TO_METHOD[name]
        response = self.provider.lifecycle(method, arguments, request_id)
        return {"tool": name, "method": method, "content": response}

    def read_resource(self, uri: str) -> dict[str, Any]:
        if uri == "exap://provider/capability/current":
            return {"uri": uri, "mimeType": "application/exap+json", "contents": self.provider.discover({})["capability"]}
        if uri == "exap://contracts/active":
            return {"uri": uri, "mimeType": "application/json", "contents": [record.contract for record in self.provider.contracts.values() if record.status == "active"]}
        raise KeyError(uri)
