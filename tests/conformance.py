#!/usr/bin/env python3
"""ExAP package conformance test.

Run from the package root:
    python tests/conformance.py
"""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.validators import validator_for
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
PACKAGE_VERSION = "0.2.0-draft"
BASE = f"https://exap.dev/schemas/{PACKAGE_VERSION}/"
RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}{': ' + detail if detail else ''}")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def walk(obj: Any) -> Iterable[Any]:
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def collect_refs(obj: Any) -> list[str]:
    refs = []
    for item in walk(obj):
        if isinstance(item, dict) and "$ref" in item:
            refs.append(item["$ref"])
    return refs


def load_schemas() -> tuple[dict[str, Any], Registry]:
    schemas = {}
    resources = []
    for p in sorted(SCHEMAS.glob("*.json")):
        data = load_json(p)
        schemas[p.name] = data
        resources.append((data["$id"], Resource.from_contents(data, default_specification=DRAFT202012)))
    return schemas, Registry().with_resources(resources)


def validate(instance: Any, schema: Any, registry: Registry) -> list[str]:
    v = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    errors = sorted(v.iter_errors(instance), key=lambda e: list(e.path))
    return [f"path={list(e.path)} message={e.message}" for e in errors]


def iter_conditions(condition: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield condition
    t = condition.get("type")
    if t in {"all", "any"}:
        for c in condition.get("conditions", []):
            yield from iter_conditions(c)
    elif t == "not":
        yield from iter_conditions(condition.get("condition", {}))
    elif t == "correlation":
        for item in condition.get("conditions", []):
            yield from iter_conditions(item.get("condition", {}))


def rule_refs(rule: dict[str, Any]) -> tuple[set[str], set[str]]:
    signals, events = set(), set()
    for c in iter_conditions(rule.get("condition", {})):
        if c.get("type") == "signal":
            signals.add(c.get("signal"))
        if c.get("type") == "event":
            events.add(c.get("event_type"))
    signals.discard(None)
    events.discard(None)
    return signals, events


def semantic_contract(contract: dict[str, Any]) -> list[str]:
    errors = []
    ids = [r.get("rule_id") for r in contract.get("rules", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate rule_id")
    scope = contract.get("scope", {})
    allowed_signals = set(scope.get("signals", []))
    allowed_events = set(scope.get("events", []))
    for rule in contract.get("rules", []):
        sigs, evs = rule_refs(rule)
        missing_sigs = sorted(sigs - allowed_signals) if allowed_signals else []
        missing_evs = sorted(evs - allowed_events) if allowed_events else []
        if missing_sigs:
            errors.append(f"rule {rule.get('rule_id')} references signals outside scope: {missing_sigs}")
        if missing_evs:
            errors.append(f"rule {rule.get('rule_id')} references events outside scope: {missing_evs}")
    return errors


def semantic_profile(profile: dict[str, Any]) -> list[str]:
    errors = []
    ids = [r.get("rule_id") for r in profile.get("rules", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate rule_id")
    allowed_signals = set(profile.get("signals", []))
    allowed_events = set(profile.get("event_types", []))
    for rule in profile.get("rules", []):
        sigs, evs = rule_refs(rule)
        if sigs - allowed_signals:
            errors.append(f"rule {rule.get('rule_id')} references undeclared signals {sorted(sigs - allowed_signals)}")
        if evs - allowed_events:
            errors.append(f"rule {rule.get('rule_id')} references undeclared events {sorted(evs - allowed_events)}")
    return errors



def profile_parameter_errors(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = {p.get("name") for p in profile.get("parameters", []) if isinstance(p, dict)}
    declared.discard(None)
    bindings = profile.get("parameter_bindings", [])
    bound = set()
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append("parameter_bindings item is not object")
            continue
        name = binding.get("parameter")
        if name not in declared:
            errors.append(f"parameter binding references undeclared parameter {name}")
        paths = binding.get("paths", [])
        if not isinstance(paths, list) or not paths:
            errors.append(f"parameter binding for {name} has no paths")
        elif any(not isinstance(path, str) or not path for path in paths):
            errors.append(f"parameter binding for {name} has invalid path")
        bound.add(name)
    declared_names = {str(name) for name in declared}
    missing = sorted(declared_names - bound)
    if missing:
        errors.append(f"declared parameters without bindings {missing}")
    return errors


def condition_operators(condition: dict[str, Any]) -> set[str]:
    operators: set[str] = set()
    for c in iter_conditions(condition):
        op = c.get("operator")
        if isinstance(op, str):
            operators.add(op)
        for f in c.get("filters", []) if isinstance(c.get("filters"), list) else []:
            fop = f.get("operator") if isinstance(f, dict) else None
            if isinstance(fop, str):
                operators.add(fop)
    return operators


def contract_operators(contract: dict[str, Any]) -> set[str]:
    operators: set[str] = set()
    for rule in contract.get("rules", []):
        operators |= condition_operators(rule.get("condition", {}))
    return operators


def capability_self_consistency_errors(capability: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    global_ops = set(capability.get("rule_capabilities", {}).get("operators", []))
    if not capability.get("rule_capabilities", {}).get("semantic_match", False) and "semantic_match" in global_ops:
        errors.append("semantic_match=false but operators include semantic_match")
    for signal in capability.get("signals", []):
        missing = sorted(set(signal.get("operators", [])) - global_ops)
        if missing:
            errors.append(f"signal {signal.get('name')} operators outside rule_capabilities {missing}")
    return errors


def capability_compatibility_errors(contract: dict[str, Any], capability: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    subject_types = {s.get("type") for s in capability.get("subject_types", [])}
    signal_specs = {s.get("name"): s for s in capability.get("signals", []) if isinstance(s, dict)}
    signals = set(signal_specs.keys())
    signal_operators = {name: set(spec.get("operators", [])) for name, spec in signal_specs.items()}
    events = {e.get("event_type") for e in capability.get("event_types", [])}
    operators = set(capability.get("rule_capabilities", {}).get("operators", []))
    aggregates = set(capability.get("rule_capabilities", {}).get("aggregates", []))
    delivery = capability.get("delivery_capabilities", {})
    modes = set(delivery.get("modes", []))
    transports = set(delivery.get("transports", []))
    content_modes = set(delivery.get("content_modes", []))

    scope = contract.get("scope", {})
    for subject in scope.get("subjects", []):
        stype = subject.get("type")
        if stype not in subject_types:
            errors.append(f"scope subject type not in capability {stype}")
    for sig in scope.get("signals", []):
        if sig not in signals:
            errors.append(f"scope signal not in capability {sig}")
    for event in scope.get("events", []):
        if event not in events:
            errors.append(f"scope event not in capability {event}")

    for rule in contract.get("rules", []):
        for sig, ev in [rule_refs(rule)]:
            for s in sorted(sig - signals):
                errors.append(f"rule {rule.get('rule_id')} signal not in capability {s}")
            for e in sorted(ev - events):
                errors.append(f"rule {rule.get('rule_id')} event not in capability {e}")
        for op in sorted(condition_operators(rule.get("condition", {})) - operators):
            errors.append(f"rule {rule.get('rule_id')} operator not in capability {op}")
        for c in iter_conditions(rule.get("condition", {})):
            if c.get("type") == "signal":
                sig = c.get("signal")
                op = c.get("operator")
                if isinstance(sig, str) and sig in signal_operators and isinstance(op, str) and op not in signal_operators[sig]:
                    errors.append(f"rule {rule.get('rule_id')} signal {sig} operator not in capability {op}")
            agg = c.get("aggregate")
            if isinstance(agg, str) and agg not in aggregates:
                errors.append(f"rule {rule.get('rule_id')} aggregate not in capability {agg}")

    contract_delivery = contract.get("delivery", {})
    for mode in contract_delivery.get("modes", []):
        if mode not in modes:
            errors.append(f"delivery mode not in capability {mode}")
    for item in contract_delivery.get("transports", []):
        t = item.get("transport")
        cm = item.get("content_mode")
        if t not in transports:
            errors.append(f"delivery transport not in capability {t}")
        if cm not in content_modes:
            errors.append(f"delivery content_mode not in capability {cm}")
    return errors


def minimal_rule(condition: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": "rule_probe",
        "name": "probe",
        "condition": condition,
        "severity": "warning",
    }



def json_pointer_get(obj: Any, pointer: str) -> Any:
    if pointer == "":
        return obj
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    cur = obj
    for raw in pointer.split("/")[1:]:
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(pointer)
    return cur


def main() -> int:
    schemas, registry = load_schemas()

    # Schema meta-validation.
    for name, schema in schemas.items():
        try:
            validator_for(schema).check_schema(schema)
            record(f"schema meta {name}", True)
        except Exception as exc:
            record(f"schema meta {name}", False, str(exc))

    # Canonical refs.
    ids = {s["$id"] for s in schemas.values()}
    for name, schema in schemas.items():
        bad = []
        for ref in collect_refs(schema):
            if ref.startswith("#"):
                continue
            base = ref.split("#", 1)[0]
            if not base.startswith(BASE):
                bad.append(f"non-canonical ref {ref}")
            elif base not in ids:
                bad.append(f"unresolved ref {ref}")
        record(f"canonical refs {name}", not bad, "; ".join(bad))

    # Valid examples.
    mappings = {
        "01-process-wait-contract.json": "exap-attention-contract.schema.json",
        "02-gpu-idle-attention-event.json": "exap-attention-event.schema.json",
        "03-email-important-contract.json": "exap-attention-contract.schema.json",
        "04-mail-attention-event.json": "exap-attention-event.schema.json",
        "05-provider-capability-process.json": "exap-capability.schema.json",
        "06-provider-capability-mail.json": "exap-capability.schema.json",
        "07-http-contract-create-request.json": "exap-lifecycle-message.schema.json",
    }
    for fn, schema_name in mappings.items():
        inst = load_json(ROOT / "examples" / fn)
        errs = validate(inst, schemas[schema_name], registry)
        sem = []
        if schema_name == "exap-attention-contract.schema.json" and not errs:
            sem = semantic_contract(inst)
        record(f"valid example {fn}", not errs and not sem, "; ".join(errs + sem))

    # MCP tools JSON: validate tool input schemas.
    mcp = load_json(ROOT / "examples" / "08-mcp-tools.json")
    tool_errors = []
    for tool in mcp.get("tools", []):
        try:
            Draft202012Validator.check_schema(tool["inputSchema"])
        except Exception as exc:
            tool_errors.append(f"{tool.get('name')}: inputSchema {exc}")
        if "outputSchema" not in tool:
            tool_errors.append(f"{tool.get('name')}: missing outputSchema")
        else:
            try:
                Draft202012Validator.check_schema(tool["outputSchema"])
            except Exception as exc:
                tool_errors.append(f"{tool.get('name')}: outputSchema {exc}")
        for ref in collect_refs(tool):
            if ref.startswith("https://exap.dev/schemas/") and not ref.startswith(BASE):
                tool_errors.append(f"{tool.get('name')}: unversioned schema ref {ref}")
    required_tools = {"exap_discover", "exap_contract_create", "exap_wait", "exap_status", "exap_attention_ack", "exap_contract_revoke"}
    seen_tools = {t.get("name") for t in mcp.get("tools", [])}
    missing_tools = sorted(required_tools - seen_tools)
    if missing_tools:
        tool_errors.append(f"missing MCP tools {missing_tools}")
    by_name = {t.get("name"): t for t in mcp.get("tools", [])}
    expected_mcp_refs = {
        "exap_discover": ("DiscoverParams", "DiscoverResult"),
        "exap_contract_create": ("ContractCreateParams", "ContractCreateResult"),
        "exap_wait": ("WaitParams", "WaitResult"),
        "exap_status": ("StatusParams", "StatusResult"),
        "exap_attention_ack": ("AttentionAckParams", "AttentionAckResult"),
        "exap_contract_revoke": ("ContractRevokeParams", "ContractRevokeResult"),
    }
    for tool_name, (params_def, result_def) in expected_mcp_refs.items():
        tool = by_name.get(tool_name, {})
        if tool.get("inputSchema", {}).get("$ref") != BASE + f"exap-lifecycle-message.schema.json#/$defs/{params_def}":
            tool_errors.append(f"{tool_name}: inputSchema must ref {params_def}")
        if tool.get("outputSchema", {}).get("$ref") != BASE + f"exap-lifecycle-message.schema.json#/$defs/{result_def}":
            tool_errors.append(f"{tool_name}: outputSchema must ref {result_def}")
    def tool_input_properties(tool_name: str) -> dict[str, Any]:
        schema = by_name.get(tool_name, {}).get("inputSchema", {})
        ref = schema.get("$ref") if isinstance(schema, dict) else None
        if isinstance(ref, str) and ref.startswith(BASE + "exap-lifecycle-message.schema.json#/$defs/"):
            def_name = ref.rsplit("/", 1)[-1]
            schema = schemas["exap-lifecycle-message.schema.json"].get("$defs", {}).get(def_name, {})
        return schema.get("properties", {}) if isinstance(schema, dict) else {}
    create_props = tool_input_properties("exap_contract_create")
    for field in ["validate_only", "idempotency_key"]:
        if field not in create_props:
            tool_errors.append(f"exap_contract_create: missing {field}")
    wait_props = tool_input_properties("exap_wait")
    if "cursor" not in wait_props:
        tool_errors.append("exap_wait: missing cursor")
    ack_props = tool_input_properties("exap_attention_ack")
    for field in ["actor", "comment"]:
        if field not in ack_props:
            tool_errors.append(f"exap_attention_ack: missing {field}")
    record("MCP tools example", not tool_errors, "; ".join(tool_errors))

    # A2A Agent Card minimum checks.
    a2a = load_json(ROOT / "examples" / "09-a2a-agent-card.json")
    a2a_errors = []
    for field in ["name", "description", "url", "version", "capabilities", "skills"]:
        if field not in a2a:
            a2a_errors.append(f"missing {field}")
    if "application/exap+json" not in a2a.get("defaultOutputModes", []):
        a2a_errors.append("defaultOutputModes must include application/exap+json")
    skill_ids = {s.get("id") for s in a2a.get("skills", [])}
    for sid in ["create_attention_contract", "wait_for_attention", "ack_attention_event", "revoke_attention_contract"]:
        if sid not in skill_ids:
            a2a_errors.append(f"missing skill {sid}")
    for skill in a2a.get("skills", []):
        if skill.get("id") == "create_attention_contract" and "text/plain" in skill.get("inputModes", []):
            nl = skill.get("x-exap-natural-language")
            if not isinstance(nl, dict) or nl.get("mode") != "validate_only_draft":
                a2a_errors.append("natural language create must be validate_only_draft")
            if nl and nl.get("active_contract_creation") is not False:
                a2a_errors.append("natural language create must not directly create active contracts")
    if not a2a.get("x-exap", {}).get("capability_ref"):
        a2a_errors.append("missing x-exap capability_ref")
    expected_a2a_refs = {
        "create_attention_contract": ("ContractCreateParams", "ContractCreateResult"),
        "wait_for_attention": ("WaitParams", "WaitResult"),
        "ack_attention_event": ("AttentionAckParams", "AttentionAckResult"),
        "revoke_attention_contract": ("ContractRevokeParams", "ContractRevokeResult"),
    }
    skills_by_id = {skill.get("id"): skill for skill in a2a.get("skills", [])}
    for skill_id, (params_def, result_def) in expected_a2a_refs.items():
        skill = skills_by_id.get(skill_id, {})
        if skill.get("x-exap-input-schema", {}).get("$ref") != BASE + f"exap-lifecycle-message.schema.json#/$defs/{params_def}":
            a2a_errors.append(f"{skill_id}: x-exap-input-schema must ref {params_def}")
        if skill.get("x-exap-output-schema", {}).get("$ref") != BASE + f"exap-lifecycle-message.schema.json#/$defs/{result_def}":
            a2a_errors.append(f"{skill_id}: x-exap-output-schema must ref {result_def}")
    record("A2A agent card example", not a2a_errors, "; ".join(a2a_errors))

    # Profiles.
    for p in sorted((ROOT / "profiles").glob("*.json")):
        inst = load_json(p)
        errs = validate(inst, schemas["exap-profile.schema.json"], registry)
        sem = [] if errs else semantic_profile(inst) + profile_parameter_errors(inst)
        record(f"profile {p.name}", not errs and not sem, "; ".join(errs + sem))



    # Profile instantiation fixtures.
    inst_errors = []
    inst_dir = ROOT / "tests" / "fixtures" / "profile-instantiations"
    fixtures = sorted(inst_dir.glob("*.json")) if inst_dir.exists() else []
    if not fixtures:
        inst_errors.append("missing profile instantiation fixtures")
    for fixture_path in fixtures:
        fixture = load_json(fixture_path)
        rel = fixture_path.relative_to(ROOT)
        for field in ["profile_file", "capability_file", "effective_contract_file", "params"]:
            if field not in fixture:
                inst_errors.append(f"{rel} missing {field}")
        if inst_errors and any(str(rel) in e for e in inst_errors):
            continue
        try:
            profile = load_json(ROOT / fixture["profile_file"])
            capability = load_json(ROOT / fixture["capability_file"])
            effective = load_json(ROOT / fixture["effective_contract_file"])
        except Exception as exc:
            inst_errors.append(f"{rel} load failed {exc}")
            continue
        errs = validate(profile, schemas["exap-profile.schema.json"], registry)
        errs += validate(capability, schemas["exap-capability.schema.json"], registry)
        errs += validate(effective, schemas["exap-attention-contract.schema.json"], registry)
        errs += semantic_contract(effective) if not errs else []
        errs += capability_compatibility_errors(effective, capability) if not errs else []
        declared = {p.get("name") for p in profile.get("parameters", []) if isinstance(p, dict)}
        supplied = set(fixture.get("params", {}).keys())
        unknown = sorted(supplied - declared)
        if unknown:
            errs.append(f"params not declared by profile {unknown}")
        param_defaults = {p.get("name"): p.get("default") for p in profile.get("parameters", []) if isinstance(p, dict)}
        for binding in profile.get("parameter_bindings", []):
            name = binding.get("parameter")
            expected = fixture.get("params", {}).get(name, param_defaults.get(name))
            for pointer in binding.get("paths", []):
                try:
                    actual = json_pointer_get(effective, pointer)
                except Exception as exc:
                    errs.append(f"binding path {pointer} missing in effective contract: {exc}")
                    continue
                if actual != expected:
                    errs.append(f"binding {name} expected {expected!r} at {pointer} got {actual!r}")
        if errs:
            inst_errors.append(f"{rel}: {'; '.join(errs)}")
    record("profile instantiation fixtures", not inst_errors, "; ".join(inst_errors))

    # Package version consistency.
    version_errors = []
    for p in sorted(list((ROOT / "examples").glob("*.json")) + list((ROOT / "profiles").glob("*.json"))):
        data = load_json(p)
        rel = p.relative_to(ROOT)
        for item in walk(data):
            if not isinstance(item, dict):
                continue
            if item.get("exap_version") and item.get("exap_version") != PACKAGE_VERSION:
                version_errors.append(f"{rel} has exap_version={item.get('exap_version')}")
            if item.get("exap_versions") and item.get("exap_versions") != [PACKAGE_VERSION]:
                version_errors.append(f"{rel} has exap_versions={item.get('exap_versions')}")
    for name, schema in schemas.items():
        if not schema.get("$id", "").startswith(BASE):
            version_errors.append(f"{name} has unversioned $id {schema.get('$id')}")
    common_version = schemas["exap-common.schema.json"].get("$defs", {}).get("ExAPVersion", {})
    if common_version.get("const") != PACKAGE_VERSION:
        version_errors.append("ExAPVersion must be fixed to PACKAGE_VERSION")
    record("package version binding", not version_errors, "; ".join(version_errors))

    # Negative fixtures.
    neg_schema = {
        "invalid-missing-rules.json": "exap-attention-contract.schema.json",
        "invalid-unknown-operator.json": "exap-attention-contract.schema.json",
        "invalid-extra-field.json": "exap-attention-contract.schema.json",
        "invalid-duplicate-rule-id.json": "exap-attention-contract.schema.json",
        "invalid-triggered-empty-evidence.json": "exap-attention-event.schema.json",
    }
    for fn, schema_name in neg_schema.items():
        inst = load_json(ROOT / "tests" / "fixtures" / "negative" / fn)
        errs = validate(inst, schemas[schema_name], registry)
        sem = []
        if schema_name == "exap-attention-contract.schema.json" and not errs:
            sem = semantic_contract(inst)
        failed_as_expected = bool(errs or sem)
        record(f"negative fixture {fn}", failed_as_expected, "" if failed_as_expected else "fixture unexpectedly passed")


    # Targeted schema probes from the integrated design audit.
    lifecycle_schema = schemas["exap-lifecycle-message.schema.json"]
    lifecycle_reject = {
        "lifecycle wait rejects unknown until": {"jsonrpc": "2.0", "id": "probe", "method": "exap.wait", "params": {"contract_id": "act_probe", "until": ["made_up_reason"], "timeout": "PT1M"}},
        "lifecycle wait rejects invalid duration": {"jsonrpc": "2.0", "id": "probe", "method": "exap.wait", "params": {"contract_id": "act_probe", "until": ["attention"], "timeout": "not-a-duration"}},
        "lifecycle wait rejects empty time duration": {"jsonrpc": "2.0", "id": "probe", "method": "exap.wait", "params": {"contract_id": "act_probe", "until": ["attention"], "timeout": "PT"}},
        "lifecycle ack snooze requires snooze_for": {"jsonrpc": "2.0", "id": "probe", "method": "exap.attention.ack", "params": {"attention_id": "attn_probe", "action": "snooze"}},
        "lifecycle contract.get rejects unknown params": {"jsonrpc": "2.0", "id": "probe", "method": "exap.contract.get", "params": {"made_up": True}},
        "lifecycle response rejects arbitrary result": {"jsonrpc": "2.0", "id": "probe", "result": {"made_up": True}},
    }
    for name, inst in lifecycle_reject.items():
        errs = validate(inst, lifecycle_schema, registry)
        record(name, bool(errs), "" if errs else "probe unexpectedly passed")
    lifecycle_accept = {
        "lifecycle error accepts JSON-RPC integer code": {"jsonrpc": "2.0", "id": "probe", "error": {"code": -32602, "message": "Invalid params", "data": {"exap_code": "ExAP-4004", "field": "params.contract.rules[0]"}}},
    }
    for name, inst in lifecycle_accept.items():
        errs = validate(inst, lifecycle_schema, registry)
        record(name, not errs, "; ".join(errs))
    lifecycle_error_reject = {
        "lifecycle error requires exap_code": {"jsonrpc": "2.0", "id": "probe", "error": {"code": -32602, "message": "Invalid params", "data": {"field": "params.contract.rules[0]"}}},
    }
    for name, inst in lifecycle_error_reject.items():
        errs = validate(inst, lifecycle_schema, registry)
        record(name, bool(errs), "" if errs else "probe unexpectedly passed")

    rule_schema = schemas["exap-rule.schema.json"]
    rule_reject = {
        "rule rejects exists with value": minimal_rule({"type": "signal", "signal": "process.status", "operator": "exists", "value": "running"}),
        "rule rejects rate missing window": minimal_rule({"type": "signal", "signal": "process.cpu.percent", "operator": "rate_gt", "value": 10}),
        "rule rejects in value not array": minimal_rule({"type": "signal", "signal": "process.status", "operator": "in", "value": "running"}),
        "rule rejects event count missing value": minimal_rule({"type": "event", "event_type": "process.exited", "operator": "count_gt"}),
        "rule rejects field filter missing value": minimal_rule({"type": "event", "event_type": "log.line.appended", "operator": "field_eq", "filters": [{"path": "payload.line", "operator": "eq"}]}),
        "rule rejects state eq missing value": minimal_rule({"type": "state", "state_path": "contract.status", "operator": "eq"}),
        "rule rejects state rate missing window": minimal_rule({"type": "state", "state_path": "delivery.retry_count", "operator": "rate_gt", "value": 3}),
    }
    for name, inst in rule_reject.items():
        errs = validate(inst, rule_schema, registry)
        record(name, bool(errs), "" if errs else "probe unexpectedly passed")
    rule_accept = {
        "rule accepts semantic_match array value": minimal_rule({"type": "signal", "signal": "mail.content.semantic_intent", "operator": "semantic_match", "value": ["urgent request", "incident"]}),
        "rule accepts datetime comparison value": minimal_rule({"type": "signal", "signal": "calendar.event.starts_at", "operator": "lt", "value": "2026-05-17T13:00:00Z"}),
        "rule accepts duration comparison value": minimal_rule({"type": "signal", "signal": "calendar.event.starts_in", "operator": "lte", "value": "PT30M"}),
    }
    for name, inst in rule_accept.items():
        errs = validate(inst, rule_schema, registry)
        record(name, not errs, "; ".join(errs))

    attn_schema = schemas["exap-attention-event.schema.json"]
    attn_base = load_json(ROOT / "examples" / "02-gpu-idle-attention-event.json")
    attn_mismatch_1 = json.loads(json.dumps(attn_base))
    attn_mismatch_1["type"] = "exap.attention.summary"
    attn_mismatch_1["data"]["status"] = "triggered"
    attn_mismatch_2 = json.loads(json.dumps(attn_base))
    attn_mismatch_2["type"] = "exap.attention.triggered"
    attn_mismatch_2["data"]["status"] = "suppressed"
    for name, inst in {
        "attention event rejects summary type with triggered status": attn_mismatch_1,
        "attention event rejects triggered type with suppressed status": attn_mismatch_2,
    }.items():
        errs = validate(inst, attn_schema, registry)
        record(name, bool(errs), "" if errs else "probe unexpectedly passed")

    # Capability compatibility and self-consistency probes.
    process_contract = load_json(ROOT / "examples" / "01-process-wait-contract.json")
    process_cap = load_json(ROOT / "examples" / "05-provider-capability-process.json")
    mail_contract = load_json(ROOT / "examples" / "03-email-important-contract.json")
    mail_cap = load_json(ROOT / "examples" / "06-provider-capability-mail.json")
    pairs = [
        ("capability compatibility process example", process_contract, process_cap),
        ("capability compatibility mail example", mail_contract, mail_cap),
    ]
    for name, contract, cap in pairs:
        compat = capability_compatibility_errors(contract, cap)
        record(name, not compat, "; ".join(compat))
    for name, cap in [("capability self-consistency process", process_cap), ("capability self-consistency mail", mail_cap)]:
        cap_errors = capability_self_consistency_errors(cap)
        record(name, not cap_errors, "; ".join(cap_errors))
    bad_contract = json.loads(json.dumps(process_contract))
    bad_contract["rules"][1]["condition"]["conditions"][1]["operator"] = "contains"
    bad_compat = capability_compatibility_errors(bad_contract, process_cap)
    record("capability compatibility rejects signal-level operator", bool(bad_compat), "" if bad_compat else "probe unexpectedly passed")

    # YAML files parse and schema refs point to existing files.
    for p in sorted((ROOT / "reference").glob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            refs = [x["$ref"] for x in walk(data) if isinstance(x, dict) and "$ref" in x]
            missing = []
            for ref in refs:
                if ref.startswith("../schemas/"):
                    target = (p.parent / ref.split("#", 1)[0]).resolve()
                    if not target.exists():
                        missing.append(ref)
            if p.name == "openapi-http-binding.yaml":
                required_ops = {
                    "exapDiscover", "exapContractCreate", "exapContractGet", "exapContractList",
                    "exapContractUpdate", "exapContractPause", "exapContractResume", "exapContractRevoke",
                    "exapWait", "exapStreamOpen", "exapAttentionAck", "exapStatus", "exapObservationQuery"
                }
                seen_ops = {item.get("operationId") for item in walk(data) if isinstance(item, dict) and item.get("operationId")}
                for op in sorted(required_ops - seen_ops):
                    missing.append(f"missing operationId {op}")
                operations = {item.get("operationId"): item for item in walk(data) if isinstance(item, dict) and item.get("operationId")}
                discover_params = {param.get("name") for param in operations.get("exapDiscover", {}).get("parameters", []) if isinstance(param, dict)}
                for param in ["environment_ref", "subject_types", "profile_ids", "signals", "include_examples"]:
                    if param not in discover_params:
                        missing.append(f"exapDiscover missing query parameter {param}")
                expected_response_refs = {
                    "exapDiscover": "DiscoverResult",
                    "exapContractCreate": "ContractCreateResult",
                    "exapContractList": "ContractListResult",
                    "exapContractGet": "ContractGetResult",
                    "exapContractUpdate": "ContractUpdateResult",
                    "exapContractPause": "ContractPauseResult",
                    "exapContractResume": "ContractResumeResult",
                    "exapContractRevoke": "ContractRevokeResult",
                    "exapWait": "WaitResult",
                    "exapStatus": "StatusResult",
                    "exapAttentionAck": "AttentionAckResult",
                    "exapObservationQuery": "ObservationQueryResult",
                }
                for op_id, result_def in expected_response_refs.items():
                    op = operations.get(op_id, {})
                    refs = [ref for ref in collect_refs(op.get("responses", {})) if ref.endswith(f"#/$defs/{result_def}")]
                    if not refs:
                        missing.append(f"{op_id} response must ref {result_def}")
                expected_request_refs = {
                    "exapContractCreate": "ContractCreateParams",
                    "exapContractUpdate": "ContractUpdateParams",
                    "exapContractPause": "ContractPauseParams",
                    "exapContractResume": "ContractResumeParams",
                    "exapContractRevoke": "ContractRevokeParams",
                    "exapWait": "WaitParams",
                    "exapAttentionAck": "AttentionAckParams",
                    "exapObservationQuery": "ObservationQueryParams",
                }
                for op_id, params_def in expected_request_refs.items():
                    op = operations.get(op_id, {})
                    refs = [ref for ref in collect_refs(op.get("requestBody", {})) if ref.endswith(f"#/$defs/{params_def}")]
                    if not refs:
                        missing.append(f"{op_id} requestBody must ref {params_def}")
                for path, methods in (data.get("paths") or {}).items():
                    if path.endswith("/ack"):
                        post = methods.get("post", {}) if isinstance(methods, dict) else {}
                        if "requestBody" not in post:
                            missing.append(f"{path} missing requestBody")
            record(f"YAML reference {p.name}", not missing, "; ".join(missing))
        except Exception as exc:
            record(f"YAML reference {p.name}", False, str(exc))

    # Manifest file existence.
    manifest_text = (ROOT / "MANIFEST.md").read_text(encoding="utf-8")
    listed = re.findall(r"`([^`]+)`", manifest_text)
    missing = []
    for item in listed:
        if item.endswith("/") or item in {"0.2.0-draft"}:
            continue
        if "*" in item:
            if not list(ROOT.glob(item)):
                missing.append(item)
            continue
        if item == "tests/conformance-report.md":
            continue
        if not (ROOT / item).exists():
            missing.append(item)
    record("manifest listed files exist", not missing, ", ".join(missing))

    # Version and deprecated terms consistency in normative package files.
    text_files = list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md")) + list((ROOT / "templates").glob("*.md"))
    banned = []
    for p in text_files:
        text = p.read_text(encoding="utf-8")
        for term in ["0.1.0-draft", "triggering_rule", "建议", "SHOULD", "非目标", "non-goals", "non-goal", "43/43", "44/44", "Conformance-43"]:
            if term in text:
                banned.append(f"{p.relative_to(ROOT)} contains {term}")
    record("normative text has no banned ambiguity terms", not banned, "; ".join(banned))

    # Legacy naming consistency: the package has migrated from the old prefix to ExAP/exap.
    old = "e" + "ap"
    old_upper = "E" + "AP"
    old_title = "E" + "ap"
    wrong_title = "Ex" + "ap"
    old_long_name = "Environment" + " Awareness Protocol"
    legacy_patterns = [
        re.compile(r"\b" + old_upper + r"\b"),
        re.compile(r"\b" + old_title + r"\b"),
        re.compile(r"\b" + wrong_title + r"\b"),
        re.compile(r"\b" + old + r"[A-Za-z0-9_]*\b"),
        re.compile(old + r"://"),
        re.compile(r"application/" + old + r"\+json"),
        re.compile(old + r"\.dev"),
        re.compile(r"\." + old + r"\.json"),
        re.compile(old + r"-"),
        re.compile(old + r"_"),
        re.compile(old + r"\."),
        re.compile(old_long_name),
    ]
    legacy_hits = []
    text_suffixes = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
    for p in ROOT.rglob("*"):
        if ".git" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        if rel == "tests/conformance-report.md":
            continue
        if any(pattern.search(rel) for pattern in legacy_patterns):
            legacy_hits.append(f"path {rel}")
        if not p.is_file() or p.suffix not in text_suffixes:
            continue
        text = p.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in legacy_patterns):
                legacy_hits.append(f"{rel}:{line_no}")
                break
    record("legacy naming removed", not legacy_hits, ", ".join(legacy_hits[:50]))

    # Schema property documentation coverage.
    normative_docs = list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md", ROOT / "GLOSSARY.md"]
    doc_text = "\n".join(path.read_text(encoding="utf-8") for path in normative_docs)
    schema_props = set()
    def collect_schema_props(obj):
        if isinstance(obj, dict):
            props = obj.get("properties")
            if isinstance(props, dict):
                schema_props.update(props.keys())
            for value in obj.values():
                collect_schema_props(value)
        elif isinstance(obj, list):
            for value in obj:
                collect_schema_props(value)
    for schema in schemas.values():
        collect_schema_props(schema)
    undocumented = []
    for prop in sorted(schema_props):
        if prop == "default":
            continue
        if re.search(r"`" + re.escape(prop) + r"`|\b" + re.escape(prop) + r"\b", doc_text) is None:
            undocumented.append(prop)
    record("schema properties documented", not undocumented, ", ".join(undocumented[:50]))

    # Every JSON file parses.
    json_errors = []
    for p in ROOT.rglob("*.json"):
        try:
            load_json(p)
        except Exception as exc:
            json_errors.append(f"{p.relative_to(ROOT)}: {exc}")
    record("all JSON files parse", not json_errors, "; ".join(json_errors))

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed
    report = ROOT / "tests" / "conformance-report.md"
    lines = [
        "# ExAP Package Self-Check Report",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Total checks: {len(RESULTS)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
        "## Results",
        "",
        "| Check | Result | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in RESULTS:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail.replace('|','/')} |")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
