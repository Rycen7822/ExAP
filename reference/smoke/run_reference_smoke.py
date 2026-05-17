#!/usr/bin/env python3
"""Run smoke checks for the ExAP reference implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import argparse
import importlib.util
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference.bindings.a2a_agent import A2aAgent
from reference.bindings.http_server import HttpBinding
from reference.bindings.mcp_server import McpBinding
from reference.exapd import ReferenceProviderAdapter
from reference.exapd.common import load_json


@dataclass
class SmokeStep:
    name: str
    passed: bool
    expected: str = ""
    actual: str = ""


@dataclass
class SmokeTarget:
    name: str
    passed: bool = True
    steps: list[SmokeStep] = field(default_factory=list)

    def add(self, name: str, passed: bool, expected: str = "", actual: str = "") -> None:
        self.steps.append(SmokeStep(name, passed, expected, actual))
        self.passed = self.passed and passed


def _load_c2_runner() -> Any:
    spec = importlib.util.spec_from_file_location("exap_c2_runner", ROOT / "tests" / "provider_behavior" / "run_c2.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load C2 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


C2 = _load_c2_runner()


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def run_c2_against_reference() -> tuple[bool, str]:
    provider = ReferenceProviderAdapter()
    metadata = C2.load_case_metadata()
    results = [func(provider, metadata) for func in C2.CASE_FUNCTIONS]
    passed = all(result.passed for result in results)
    detail = f"{sum(1 for item in results if item.passed)}/{len(results)} C2 cases PASS"
    return passed, detail


def smoke_openapi() -> SmokeTarget:
    target = SmokeTarget("openapi")
    openapi = load_json_like_yaml("reference/openapi-http-binding.yaml")
    paths = set(openapi.get("paths", {}).keys())
    required_paths = {
        "/exap/capability",
        "/exap/contracts",
        "/exap/contracts/{contract_id}",
        "/exap/contracts/{contract_id}/wait",
        "/exap/contracts/{contract_id}/status",
        "/exap/attention/{attention_id}/ack",
    }
    target.add("OpenAPI includes lifecycle smoke endpoints", required_paths <= paths, str(sorted(required_paths)), str(sorted(paths & required_paths)))
    c2_ok, c2_detail = run_c2_against_reference()
    target.add("reference provider passes shared C2 runner", c2_ok, "10/10 C2 cases PASS", c2_detail)
    provider = ReferenceProviderAdapter()
    http = HttpBinding(provider)
    contract = load_json("examples/01-process-wait-contract.json")
    create = http.post_jsonrpc("exap.contract.create", {"contract": contract, "idempotency_key": "r4-openapi"}, "r4-openapi-create")
    wait = http.post_jsonrpc("exap.wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S"}, "r4-openapi-wait")
    status = http.post_jsonrpc("exap.status", {"contract_id": contract["contract_id"], "include": ["state", "metrics"]}, "r4-openapi-status")
    ack = http.post_jsonrpc("exap.attention.ack", {"attention_id": "attn_gpu_idle_001", "action": "seen"}, "r4-openapi-ack")
    revoke = http.post_jsonrpc("exap.contract.revoke", {"contract_id": contract["contract_id"], "reason": "smoke complete"}, "r4-openapi-revoke")
    ok = all(item["status"] == 200 and "result" in item["body"] for item in [create, wait, status, ack, revoke])
    target.add("HTTP create/wait/status/ack/revoke smoke", ok, "all status=200 with result", json.dumps({"create": create["status"], "wait": wait["status"], "status": status["status"], "ack": ack["status"], "revoke": revoke["status"]}, ensure_ascii=False))
    return target


def smoke_mcp() -> SmokeTarget:
    target = SmokeTarget("mcp")
    provider = ReferenceProviderAdapter()
    mcp = McpBinding(provider)
    expected_tools = {"exap_discover", "exap_contract_create", "exap_wait", "exap_status", "exap_attention_ack", "exap_contract_revoke"}
    target.add("MCP exposes six lifecycle tools", set(mcp.list_tools()) == expected_tools, str(sorted(expected_tools)), str(sorted(mcp.list_tools())))
    contract = load_json("examples/01-process-wait-contract.json")
    create = mcp.call_tool("exap_contract_create", {"contract": contract, "idempotency_key": "r4-mcp"}, "r4-mcp-create")
    wait = mcp.call_tool("exap_wait", {"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S"}, "r4-mcp-wait")
    status = mcp.call_tool("exap_status", {"contract_id": contract["contract_id"], "include": ["state", "metrics"]}, "r4-mcp-status")
    ack = mcp.call_tool("exap_attention_ack", {"attention_id": "attn_gpu_idle_001", "action": "seen"}, "r4-mcp-ack")
    revoke = mcp.call_tool("exap_contract_revoke", {"contract_id": contract["contract_id"], "reason": "smoke complete"}, "r4-mcp-revoke")
    ok = all("result" in item["content"] for item in [create, wait, status, ack, revoke])
    target.add("MCP tool calls return ExAP result envelopes", ok, "all content.result present", json.dumps({"create": "result" in create["content"], "wait": "result" in wait["content"], "status": "result" in status["content"], "ack": "result" in ack["content"], "revoke": "result" in revoke["content"]}, ensure_ascii=False))
    resource = mcp.read_resource("exap://provider/capability/current")
    target.add("MCP capability resource is readable", resource.get("contents", {}).get("capability_id") == "cap_local_process_001", "cap_local_process_001", resource.get("contents", {}).get("capability_id", ""))
    return target


def smoke_a2a() -> SmokeTarget:
    target = SmokeTarget("a2a")
    provider = ReferenceProviderAdapter()
    agent = A2aAgent(provider)
    card = agent.card()
    skills = {skill["id"] for skill in card.get("skills", [])}
    target.add("A2A card exposes create/wait/ack/revoke skills", {"create_attention_contract", "wait_for_attention", "ack_attention_event", "revoke_attention_contract"} <= skills, "four ExAP skills", str(sorted(skills)))
    draft = agent.create_contract("notify me about urgent approval requests", "r4-a2a-draft")
    target.add("A2A text/plain returns validate-only draft", draft["artifacts"][0]["data"].get("status") == "draft" and not provider.contracts, "draft and no active contract", json.dumps(draft, ensure_ascii=False)[:700])
    contract = load_json("examples/03-email-important-contract.json")
    create = agent.create_contract({"contract": contract, "idempotency_key": "r4-a2a"}, "r4-a2a-create")
    wait = agent.wait({"contract_id": contract["contract_id"], "until": ["attention"], "timeout": "PT1S"}, "r4-a2a-wait")
    ack = agent.ack({"attention_id": "attn_mail_urgent_001", "action": "seen"}, "r4-a2a-ack")
    revoke = agent.revoke({"contract_id": contract["contract_id"], "reason": "smoke complete"}, "r4-a2a-revoke")
    ok = all(task["state"] == "completed" and task["artifacts"][0]["mediaType"] == "application/exap+json" for task in [create, wait, ack, revoke])
    target.add("A2A structured JSON creates active contract and returns ExAP artifacts", ok, "completed application/exap+json artifacts", json.dumps({"create": create["state"], "wait": wait["state"], "ack": ack["state"], "revoke": revoke["state"]}, ensure_ascii=False))
    return target


def smoke_operations() -> SmokeTarget:
    target = SmokeTarget("operations")
    provider = ReferenceProviderAdapter()
    http = HttpBinding(provider)
    health = http.healthz()
    ready = http.readyz()
    metrics = http.metrics()
    dlq = http.dlq()
    expected_health = json.loads((ROOT / "reference/smoke/expected/healthz.json").read_text(encoding="utf-8"))
    expected_ready = json.loads((ROOT / "reference/smoke/expected/readyz.json").read_text(encoding="utf-8"))
    expected_metrics_tokens = (ROOT / "reference/smoke/expected/metrics.txt").read_text(encoding="utf-8").splitlines()
    target.add("/healthz returns expected body", health["status"] == 200 and health["body"] == expected_health, json.dumps(expected_health), json.dumps(health["body"], ensure_ascii=False))
    target.add("/readyz returns ready body", ready["status"] == 200 and all(ready["body"].get(k) == v for k, v in expected_ready.items()), json.dumps(expected_ready), json.dumps(ready["body"], ensure_ascii=False))
    target.add("/metrics exposes expected metric names", metrics["status"] == 200 and all(token in metrics["body"] for token in expected_metrics_tokens if token), "metric tokens present", metrics["body"])
    target.add("DLQ query returns empty queue object", dlq["status"] == 200 and dlq["body"] == {"items": [], "count": 0}, '{"items": [], "count": 0}', json.dumps(dlq["body"], ensure_ascii=False))
    return target


def load_json_like_yaml(path: str) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - repository tooling includes PyYAML for conformance.
        raise RuntimeError("PyYAML is required to load reference YAML files") from exc
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


TARGETS: dict[str, Callable[[], SmokeTarget]] = {
    "openapi": smoke_openapi,
    "mcp": smoke_mcp,
    "a2a": smoke_a2a,
    "operations": smoke_operations,
}


def write_report(path: Path, selected: list[str], results: list[SmokeTarget]) -> None:
    passed = sum(1 for result in results if result.passed)
    lines = [
        "# ExAP Reference Smoke Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Level: R4 smoke",
        f"Git commit: `{git_commit()}`",
        "ExAP version: `0.2.0-draft`",
        "Provider adapter: `reference.exapd.provider:ReferenceProviderAdapter`",
        f"Targets: {', '.join(selected)}",
        f"Summary: {passed}/{len(results)} targets PASS",
        "",
        "| Target | Status | Step count |",
        "|---|---:|---:|",
    ]
    for result in results:
        lines.append(f"| {result.name} | {'PASS' if result.passed else 'FAIL'} | {len(result.steps)} |")
    lines.extend(["", "## Details", ""])
    for result in results:
        lines.append(f"### {result.name}")
        lines.append("")
        lines.append(f"Status: {'PASS' if result.passed else 'FAIL'}")
        lines.append("")
        lines.append("| Step | Status | Expected | Actual |")
        lines.append("|---|---:|---|---|")
        for step in result.steps:
            lines.append(f"| {step.name} | {'PASS' if step.passed else 'FAIL'} | {step.expected.replace('|', '/')} | {step.actual.replace('|', '/')} |")
        lines.append("")
    lines.extend([
        "## Rerun",
        "",
        "```bash",
        f"python reference/smoke/run_reference_smoke.py --target {'all' if set(selected) == set(TARGETS) else ','.join(selected)} --report {path.as_posix()}",
        "```",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def selected_targets(value: str) -> list[str]:
    if value == "all":
        return list(TARGETS)
    targets = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [item for item in targets if item not in TARGETS]
    if unknown:
        raise SystemExit(f"Unknown target(s): {', '.join(unknown)}")
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ExAP reference smoke checks")
    parser.add_argument("--target", default="all", help="all, openapi, mcp, a2a, operations, or comma-separated list")
    parser.add_argument("--report", default="reference/smoke/reports/reference-smoke-report.md")
    args = parser.parse_args()
    selected = selected_targets(args.target)
    results = [TARGETS[target]() for target in selected]
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    write_report(report_path, selected, results)
    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.name}")
        for step in result.steps:
            if not step.passed:
                print(f"  - {step.name}: expected {step.expected}; actual {step.actual}")
    failed = [result for result in results if not result.passed]
    print(f"Reference smoke: {len(results) - len(failed)}/{len(results)} targets PASS")
    print(f"Report: {report_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
