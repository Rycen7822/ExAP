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
from jsonschema import Draft202012Validator
from jsonschema.validators import validator_for
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
BASE = "https://exap.dev/schemas/"
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
    v = Draft202012Validator(schema, registry=registry)
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
            tool_errors.append(f"{tool.get('name')}: {exc}")
    required_tools = {"exap_discover", "exap_contract_create", "exap_wait", "exap_status", "exap_attention_ack", "exap_contract_revoke"}
    seen_tools = {t.get("name") for t in mcp.get("tools", [])}
    missing_tools = sorted(required_tools - seen_tools)
    if missing_tools:
        tool_errors.append(f"missing MCP tools {missing_tools}")
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
    for sid in ["create_attention_contract", "wait_for_attention"]:
        if sid not in skill_ids:
            a2a_errors.append(f"missing skill {sid}")
    record("A2A agent card example", not a2a_errors, "; ".join(a2a_errors))

    # Profiles.
    for p in sorted((ROOT / "profiles").glob("*.json")):
        inst = load_json(p)
        errs = validate(inst, schemas["exap-profile.schema.json"], registry)
        sem = [] if errs else semantic_profile(inst)
        record(f"profile {p.name}", not errs and not sem, "; ".join(errs + sem))

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
        for term in ["0.1.0-draft", "triggering_rule", "建议", "SHOULD"]:
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
        "# ExAP Conformance Report",
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
