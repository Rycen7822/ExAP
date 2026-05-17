#!/usr/bin/env python3
"""Run the ExAP C2 Provider behavior suite."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import argparse
import importlib
import importlib.util
import json
import subprocess
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tests.provider_behavior.adapter import ROOT, clone_json, load_json
else:
    from .adapter import ROOT, clone_json, load_json


@dataclass
class StepResult:
    name: str
    passed: bool
    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    expected: str = ""
    actual: str = ""


@dataclass
class CaseResult:
    case_id: str
    name: str
    passed: bool = True
    steps: list[StepResult] = field(default_factory=list)

    def add(self, step: StepResult) -> None:
        self.steps.append(step)
        self.passed = self.passed and step.passed


def load_conformance_helpers() -> Any:
    spec = importlib.util.spec_from_file_location("exap_conformance_helpers", ROOT / "tests" / "conformance.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load tests/conformance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONF = load_conformance_helpers()
SCHEMAS, REGISTRY = CONF.load_schemas()
LIFECYCLE_SCHEMA = SCHEMAS["exap-lifecycle-message.schema.json"]
ATTENTION_EVENT_SCHEMA = SCHEMAS["exap-attention-event.schema.json"]
OBSERVATION_SCHEMA = SCHEMAS["exap-observation.schema.json"]


def import_adapter(spec: str) -> Any:
    module_name, _, class_name = spec.partition(":")
    if not module_name or not class_name:
        raise SystemExit("--adapter must use module.path:ClassName")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls()


def validate_instance(instance: Any, schema: dict[str, Any]) -> list[str]:
    return CONF.validate(instance, schema, REGISTRY)


def request_for(method: str, params: dict[str, Any], request_id: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}


def call_lifecycle(adapter: Any, method: str, params: dict[str, Any], request_id: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    request = request_for(method, params, request_id)
    request_errors = validate_instance(request, LIFECYCLE_SCHEMA)
    if request_errors:
        return request, {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32600, "message": "request failed local schema validation", "data": {"exap_code": "ExAP-4000", "field": "; ".join(request_errors)}}}, request_errors
    response = adapter.lifecycle(method, params, request_id)
    response_errors = validate_instance(response, LIFECYCLE_SCHEMA)
    return request, response, response_errors


def assert_step(
    case: CaseResult,
    name: str,
    condition: bool,
    *,
    request: dict[str, Any] | None = None,
    response: dict[str, Any] | None = None,
    expected: str = "",
    actual: str = "",
) -> None:
    case.add(StepResult(name=name, passed=condition, request=request, response=response, expected=expected, actual=actual))


def assert_lifecycle_ok(case: CaseResult, adapter: Any, method: str, params: dict[str, Any], request_id: str) -> dict[str, Any]:
    request, response, errors = call_lifecycle(adapter, method, clone_json(params), request_id)
    assert_step(case, f"{method} schema-valid success envelope", not errors and "result" in response, request=request, response=response, expected="valid success response", actual="; ".join(errors) if errors else "valid")
    return response


def assert_lifecycle_error(case: CaseResult, adapter: Any, method: str, params: dict[str, Any], request_id: str, code: int, exap_code: str) -> dict[str, Any]:
    request, response, errors = call_lifecycle(adapter, method, clone_json(params), request_id)
    err = response.get("error", {})
    ok = not errors and err.get("code") == code and err.get("data", {}).get("exap_code") == exap_code and "retryable" in err.get("data", {})
    assert_step(case, f"{method} maps error {exap_code}", ok, request=request, response=response, expected=f"code={code}, exap_code={exap_code}, retryable present", actual="; ".join(errors) if errors else json.dumps(err, ensure_ascii=False, sort_keys=True))
    return response


def load_case_metadata() -> dict[str, dict[str, Any]]:
    cases_dir = ROOT / "tests" / "provider_behavior" / "cases"
    metadata = {}
    for path in sorted(cases_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        metadata[data["case_id"]] = data
    return metadata


def case_discover(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-00", meta["C2-00"]["name"])
    response = assert_lifecycle_ok(case, adapter, "exap.discover", {}, "c2-00-default")
    capability = response.get("result", {}).get("capability", {})
    assert_step(case, "discover returns package version", "0.2.0-draft" in capability.get("exap_versions", []), response=response, expected="0.2.0-draft in exap_versions", actual=str(capability.get("exap_versions")))
    assert_step(case, "discover exposes signals/events/operators/delivery/profiles", all(capability.get(key) for key in ["signals", "event_types", "profiles"]) and bool(capability.get("rule_capabilities", {}).get("operators")) and bool(capability.get("delivery_capabilities", {}).get("modes")), response=response, expected="non-empty capability surfaces", actual=json.dumps({k: bool(capability.get(k)) for k in ["signals", "event_types", "profiles", "rule_capabilities", "delivery_capabilities"]}, ensure_ascii=False))
    mail = assert_lifecycle_ok(case, adapter, "exap.discover", {"profile_ids": ["profile:email-priority"]}, "c2-00-mail")
    assert_step(case, "discover profile filter returns mail capability", mail.get("result", {}).get("capability", {}).get("capability_id") == "cap_mail_001", response=mail, expected="cap_mail_001", actual=mail.get("result", {}).get("capability", {}).get("capability_id", ""))
    return case


def case_create_validate_only(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-01", meta["C2-01"]["name"])
    before = len(adapter.contracts)
    contract = load_json("examples/01-process-wait-contract.json")
    response = assert_lifecycle_ok(case, adapter, "exap.contract.create", {"contract": contract, "validate_only": True}, "c2-01")
    result = response.get("result", {})
    assert_step(case, "validate_only returns draft effective contract", result.get("status") == "draft" and result.get("effective_contract", {}).get("contract_id") == contract["contract_id"], response=response, expected="draft and same contract_id", actual=json.dumps(result, ensure_ascii=False)[:500])
    assert_step(case, "validate_only does not mutate provider state", len(adapter.contracts) == before, response=response, expected=f"contract count {before}", actual=str(len(adapter.contracts)))
    return case


def case_create_idempotent(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-02", meta["C2-02"]["name"])
    contract = load_json("examples/01-process-wait-contract.json")
    params = {"contract": contract, "idempotency_key": "idem-process-001"}
    first = assert_lifecycle_ok(case, adapter, "exap.contract.create", params, "c2-02-a")
    second = assert_lifecycle_ok(case, adapter, "exap.contract.create", params, "c2-02-b")
    first_id = first.get("result", {}).get("contract_id")
    second_id = second.get("result", {}).get("contract_id")
    assert_step(case, "idempotent create returns same contract_id", first_id == second_id == "act_process_wait_001", response=second, expected="act_process_wait_001 twice", actual=f"{first_id}, {second_id}")
    assert_step(case, "created contract is active", adapter.snapshot_state("act_process_wait_001").get("status") == "active", response=first, expected="active", actual=json.dumps(adapter.snapshot_state("act_process_wait_001"), ensure_ascii=False))
    return case


def case_get_list_status(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-03", meta["C2-03"]["name"])
    get_response = assert_lifecycle_ok(case, adapter, "exap.contract.get", {"contract_id": "act_process_wait_001", "include_state": True}, "c2-03-get")
    list_response = assert_lifecycle_ok(case, adapter, "exap.contract.list", {"status": ["active"], "limit": 10}, "c2-03-list")
    status_response = assert_lifecycle_ok(case, adapter, "exap.status", {"contract_id": "act_process_wait_001", "include": ["state", "metrics", "recent_events"]}, "c2-03-status")
    assert_step(case, "get/list/status agree on contract_id", get_response["result"]["contract"]["contract_id"] == "act_process_wait_001" and any(c["contract_id"] == "act_process_wait_001" for c in list_response["result"]["contracts"]) and status_response["result"]["contract_id"] == "act_process_wait_001", response=status_response, expected="same contract_id across methods", actual=json.dumps({"get": get_response["result"]["contract"]["contract_id"], "list_count": len(list_response["result"]["contracts"]), "status": status_response["result"]["contract_id"]}, ensure_ascii=False))
    return case


def case_update_pause_resume_revoke(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-04", meta["C2-04"]["name"])
    contract = load_json("examples/03-email-important-contract.json")
    assert_lifecycle_ok(case, adapter, "exap.contract.create", {"contract": contract, "idempotency_key": "idem-mail-001"}, "c2-04-create")
    update = assert_lifecycle_ok(case, adapter, "exap.contract.update", {"contract_id": "act_email_priority_001", "patch": {"intent": "surface_important_email_with_runtime_update"}, "expected_version": "1"}, "c2-04-update")
    pause = assert_lifecycle_ok(case, adapter, "exap.contract.pause", {"contract_id": "act_email_priority_001", "reason": "operator requested"}, "c2-04-pause")
    resume = assert_lifecycle_ok(case, adapter, "exap.contract.resume", {"contract_id": "act_email_priority_001", "reason": "operator resumed"}, "c2-04-resume")
    revoke = assert_lifecycle_ok(case, adapter, "exap.contract.revoke", {"contract_id": "act_email_priority_001", "reason": "case completed"}, "c2-04-revoke")
    assert_step(case, "update/pause/resume/revoke statuses are deterministic", update["result"]["status"] == "active" and pause["result"]["status"] == "paused" and resume["result"]["status"] == "active" and revoke["result"]["status"] == "revoked", response=revoke, expected="active -> paused -> active -> revoked", actual=json.dumps([update["result"]["status"], pause["result"]["status"], resume["result"]["status"], revoke["result"]["status"]], ensure_ascii=False))
    return case


def case_wait(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-05", meta["C2-05"]["name"])
    timeout = assert_lifecycle_ok(case, adapter, "exap.wait", {"contract_id": "act_process_wait_001", "until": ["timeout"], "timeout": "PT1S", "include": ["state"]}, "c2-05-timeout")
    attention = assert_lifecycle_ok(case, adapter, "exap.wait", {"contract_id": "act_process_wait_001", "until": ["attention"], "timeout": "PT1S", "include": ["event", "state"], "cursor": "cursor_start"}, "c2-05-attention")
    interrupted = assert_lifecycle_ok(case, adapter, "exap.wait", {"contract_id": "act_process_wait_001", "until": ["interrupted"], "timeout": "PT1S"}, "c2-05-interrupted")
    event_errors = validate_instance(attention["result"].get("event"), ATTENTION_EVENT_SCHEMA)
    assert_step(case, "wait covers timeout attention interrupted", [timeout["result"]["return_reason"], attention["result"]["return_reason"], interrupted["result"]["return_reason"]] == ["timeout", "attention", "interrupted"] and not event_errors, response=attention, expected="three return reasons and valid event", actual="; ".join(event_errors) if event_errors else "valid")
    return case


def case_stream(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-06", meta["C2-06"]["name"])
    response = assert_lifecycle_ok(case, adapter, "exap.stream.open", {"contract_id": "act_process_wait_001", "include": ["event"], "cursor": "cursor_start"}, "c2-06-open")
    stream = adapter.open_stream({"contract_id": "act_process_wait_001", "include": ["event"], "cursor": "cursor_start"})
    frame_types = [frame.get("type") for frame in stream.get("frames", [])]
    event_frame = next((frame for frame in stream.get("frames", []) if frame.get("type") == "event"), {})
    event_errors = validate_instance(event_frame.get("event"), ATTENTION_EVENT_SCHEMA)
    assert_step(case, "stream metadata and keepalive/event/error frames", response["result"]["stream_id"] == stream["metadata"]["stream_id"] and frame_types == ["keepalive", "event", "error"] and not event_errors, response=response, expected="metadata plus keepalive/event/error", actual=json.dumps({"metadata": stream.get("metadata"), "frame_types": frame_types, "event_errors": event_errors}, ensure_ascii=False))
    return case


def case_ack(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-07", meta["C2-07"]["name"])
    expected = {"seen": "acknowledged", "snooze": "snoozed", "dismiss": "dismissed", "escalate": "escalated"}
    actual = {}
    for action, status in expected.items():
        params = {"attention_id": "attn_gpu_idle_001", "action": action, "actor": "agent:test"}
        if action == "snooze":
            params["snooze_for"] = "PT10M"
        response = assert_lifecycle_ok(case, adapter, "exap.attention.ack", params, f"c2-07-{action}")
        actual[action] = response.get("result", {}).get("status")
    assert_step(case, "ack actions map to stable statuses", actual == expected, expected=json.dumps(expected, ensure_ascii=False), actual=json.dumps(actual, ensure_ascii=False))
    return case


def case_observation_query(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-08", meta["C2-08"]["name"])
    response = assert_lifecycle_ok(case, adapter, "exap.observation.query", {"contract_id": "act_process_wait_001", "subject_ref": "exap://local/gpu/0", "signal": "gpu.util.percent", "limit": 10}, "c2-08")
    items = response.get("result", {}).get("items", [])
    item_errors = []
    for item in items:
        item_errors.extend(validate_instance(item, OBSERVATION_SCHEMA))
    assert_step(case, "observation.query returns schema-valid paginated items", len(items) == 1 and not item_errors, response=response, expected="one gpu.util.percent item", actual="; ".join(item_errors) if item_errors else json.dumps(items, ensure_ascii=False))
    return case


def case_error_mapping(adapter: Any, meta: dict[str, Any]) -> CaseResult:
    case = CaseResult("C2-09", meta["C2-09"]["name"])
    assert_lifecycle_error(case, adapter, "exap.contract.get", {"contract_id": "act_missing"}, "c2-09-missing", -32004, "ExAP-4040")
    bad = load_json("examples/01-process-wait-contract.json")
    bad["contract_id"] = "act_bad_signal_001"
    bad["scope"]["signals"].append("made.up.signal")
    bad["rules"][0]["condition"]["type"] = "signal"
    bad["rules"][0]["condition"].pop("event_type", None)
    bad["rules"][0]["condition"]["signal"] = "made.up.signal"
    bad["rules"][0]["condition"]["operator"] = "eq"
    bad["rules"][0]["condition"]["value"] = 1
    assert_lifecycle_error(case, adapter, "exap.contract.create", {"contract": bad}, "c2-09-unsupported-signal", -32602, "ExAP-4006")
    nested_bad = load_json("examples/01-process-wait-contract.json")
    nested_bad["contract_id"] = "act_bad_nested_signal_001"
    nested_bad["rules"][1]["condition"]["conditions"][1]["signal"] = "made.up.signal"
    assert_lifecycle_error(case, adapter, "exap.contract.create", {"contract": nested_bad}, "c2-09-nested-unsupported-signal", -32602, "ExAP-4006")
    event_bad = load_json("examples/01-process-wait-contract.json")
    event_bad["contract_id"] = "act_bad_scope_event_001"
    event_bad["scope"]["events"].append("made.up.event")
    assert_lifecycle_error(case, adapter, "exap.contract.create", {"contract": event_bad}, "c2-09-unsupported-scope-event", -32602, "ExAP-4006")
    assert_lifecycle_error(case, adapter, "exap.contract.update", {"contract_id": "act_process_wait_001", "patch": {"intent": "conflict"}, "expected_version": "999"}, "c2-09-conflict", -32009, "ExAP-4090")
    return case


CASE_FUNCTIONS: list[Callable[[Any, dict[str, dict[str, Any]]], CaseResult]] = [
    case_discover,
    case_create_validate_only,
    case_create_idempotent,
    case_get_list_status,
    case_update_pause_resume_revoke,
    case_wait,
    case_stream,
    case_ack,
    case_observation_query,
    case_error_mapping,
]


def compact_json(value: Any, limit: int = 900) -> str:
    if value is None:
        return ""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def current_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def write_report(path: Path, adapter_spec: str, results: list[CaseResult]) -> None:
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    lines = [
        "# ExAP C2 Provider Behavior Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Level: C2",
        f"Git commit: `{current_commit()}`",
        "ExAP version: `0.2.0-draft`",
        f"Adapter: `{adapter_spec}`",
        f"Summary: {passed}/{total} cases PASS",
        "",
        "| Case | Status | Step count |",
        "|---|---:|---:|",
    ]
    for result in results:
        lines.append(f"| {result.case_id} {result.name} | {'PASS' if result.passed else 'FAIL'} | {len(result.steps)} |")
    lines.extend(["", "## Case Details", ""])
    for result in results:
        lines.append(f"### {result.case_id}. {result.name}")
        lines.append("")
        lines.append(f"Status: {'PASS' if result.passed else 'FAIL'}")
        lines.append("")
        lines.append("| Step | Status | Expected | Actual |")
        lines.append("|---|---:|---|---|")
        for step in result.steps:
            actual = (step.actual or compact_json(step.response)).replace("|", "/")
            expected = step.expected.replace("|", "/")
            lines.append(f"| {step.name} | {'PASS' if step.passed else 'FAIL'} | {expected} | {actual} |")
        lines.append("")
    lines.extend([
        "## Rerun",
        "",
        "```bash",
        f"python tests/provider_behavior/run_c2.py --adapter {adapter_spec} --report {path.as_posix()}",
        "```",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ExAP C2 provider behavior suite")
    parser.add_argument("--adapter", required=True, help="Adapter class as module.path:ClassName")
    parser.add_argument("--report", default="tests/provider_behavior/reports/c2-report.md", help="Markdown report path")
    args = parser.parse_args()

    adapter = import_adapter(args.adapter)
    metadata = load_case_metadata()
    results = [func(adapter, metadata) for func in CASE_FUNCTIONS]
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    write_report(report_path, args.adapter, results)
    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.case_id} {result.name}")
        for step in result.steps:
            if not step.passed:
                print(f"  - {step.name}: expected {step.expected}; actual {step.actual or compact_json(step.response)}")
    failed = [result for result in results if not result.passed]
    print(f"C2 Provider Behavior: {len(results) - len(failed)}/{len(results)} cases PASS")
    print(f"Report: {report_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
