#!/usr/bin/env python3
"""Shared evaluator logic for ExAP C3 profile transcript checks."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import importlib.util
import json
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def load_json(relative_path: str | Path) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_conformance_helpers() -> Any:
    spec = importlib.util.spec_from_file_location("exap_conformance_helpers", ROOT / "tests" / "conformance.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load tests/conformance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONF = load_conformance_helpers()
SCHEMAS, REGISTRY = CONF.load_schemas()
FIXTURE_SCHEMA = load_json("tests/profile_evaluation/transcript_schema.json")


@dataclass
class EvaluationResult:
    case_id: str
    name: str
    passed: bool = True
    details: list[dict[str, str]] = field(default_factory=list)
    coverage: set[str] = field(default_factory=set)

    def check(self, name: str, condition: bool, expected: str, actual: str) -> None:
        self.details.append({"name": name, "status": "PASS" if condition else "FAIL", "expected": expected, "actual": actual})
        self.passed = self.passed and condition


def json_pointer_get(document: Any, pointer: str) -> Any:
    current = document
    if pointer == "":
        return current
    for raw_part in pointer.strip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


class ProfileTranscriptEvaluator:
    def evaluate_file(self, path: Path) -> EvaluationResult:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        return self.evaluate(fixture, path)

    def evaluate(self, fixture: dict[str, Any], path: Path) -> EvaluationResult:
        result = EvaluationResult(case_id=fixture.get("case_id", path.stem), name=fixture.get("name", path.stem))
        self._validate_fixture_schema(fixture, result)
        profile = load_json(fixture["profile_file"])
        capability = load_json(fixture["capability_file"])
        contract = load_json(fixture["effective_contract_file"])
        self._check_profile_params(profile, contract, fixture["params"], result)
        contract_errors = CONF.validate(contract, SCHEMAS["exap-attention-contract.schema.json"], REGISTRY)
        semantic_errors = CONF.semantic_contract(contract) if not contract_errors else []
        compatibility_errors = CONF.capability_compatibility_errors(contract, capability) if not contract_errors else []
        coverage = self._derive_coverage(fixture, contract, compatibility_errors)
        self._check_declared_coverage(fixture, coverage, result)
        result.coverage.update(coverage)
        if fixture["expected_result"] == "pass":
            result.check("effective contract schema-valid", not contract_errors, "no schema errors", "; ".join(contract_errors))
            result.check("effective contract semantic-valid", not semantic_errors, "no semantic errors", "; ".join(semantic_errors))
            result.check("effective contract capability-compatible", not compatibility_errors, "no compatibility errors", "; ".join(compatibility_errors))
            self._check_attention_events(fixture, result)
            self._check_machine_assertable_outputs(fixture, result)
            self._check_transcript_alignment(fixture, result)
            self._check_transcript_order(fixture, result)
        else:
            result.check("capability mismatch is detected", bool(compatibility_errors), "compatibility errors present", "; ".join(compatibility_errors))
            result.check("negative transcript emits no attention event", not fixture.get("expected_attention_events"), "no expected attention events", str(len(fixture.get("expected_attention_events", []))))
        return result

    def _validate_fixture_schema(self, fixture: dict[str, Any], result: EvaluationResult) -> None:
        errors = sorted(Draft202012Validator(FIXTURE_SCHEMA).iter_errors(fixture), key=lambda e: list(e.path))
        result.check("fixture schema-valid", not errors, "no fixture schema errors", "; ".join(error.message for error in errors))

    def _check_profile_params(self, profile: dict[str, Any], contract: dict[str, Any], params: dict[str, Any], result: EvaluationResult) -> None:
        declared = {param["name"]: param for param in profile.get("parameters", [])}
        missing_required = [name for name, param in declared.items() if param.get("required") and name not in params and "default" not in param]
        result.check("profile required params resolved", not missing_required, "all required params/defaults present", ", ".join(missing_required))
        mismatches = []
        for binding in profile.get("parameter_bindings", []):
            name = binding["parameter"]
            expected = params.get(name, declared.get(name, {}).get("default"))
            for pointer in binding.get("paths", []):
                actual = json_pointer_get(contract, pointer)
                if actual != expected:
                    mismatches.append(f"{name}@{pointer}: expected {expected!r}, got {actual!r}")
        result.check("profile parameter bindings applied", not mismatches, "bound paths equal params/defaults", "; ".join(mismatches))

    def _check_attention_events(self, fixture: dict[str, Any], result: EvaluationResult) -> None:
        event_errors = []
        for event in fixture.get("expected_attention_events", []):
            event_errors.extend(CONF.validate(event, SCHEMAS["exap-attention-event.schema.json"], REGISTRY))
        result.check("expected Attention Events schema-valid", not event_errors and bool(fixture.get("expected_attention_events")), "non-empty schema-valid events", "; ".join(event_errors))

    def _check_machine_assertable_outputs(self, fixture: dict[str, Any], result: EvaluationResult) -> None:
        suppressed_ok = all("reason" in item and "dedupe_key" in item for item in fixture.get("expected_suppressed_events", []))
        transitions_ok = all("contract_id" in item and "from" in item and "to" in item and "action" in item for item in fixture.get("expected_state_transitions", []))
        delivery_ok = all("mode" in item and "transport" in item and "success" in item for item in fixture.get("expected_delivery_reports", []))
        result.check("suppressed/internal events are machine-assertable", suppressed_ok, "reason and dedupe_key present", json.dumps(fixture.get("expected_suppressed_events", []), ensure_ascii=False))
        result.check("state transitions are machine-assertable", transitions_ok, "contract_id/from/to/action present", json.dumps(fixture.get("expected_state_transitions", []), ensure_ascii=False))
        result.check("delivery reports are machine-assertable", delivery_ok, "mode/transport/success present", json.dumps(fixture.get("expected_delivery_reports", []), ensure_ascii=False))

    def _derive_coverage(self, fixture: dict[str, Any], contract: dict[str, Any], compatibility_errors: list[str]) -> set[str]:
        coverage: set[str] = set()
        for rule in contract.get("rules", []):
            condition = rule.get("condition", {})
            for item in CONF.iter_conditions(condition):
                condition_type = item.get("type")
                operator = item.get("operator", "")
                if condition_type == "signal":
                    coverage.add("signal_condition")
                if condition_type == "event":
                    coverage.add("event_condition")
                if condition_type == "state":
                    coverage.add("state_condition")
                if condition_type == "correlation":
                    coverage.add("correlation_condition")
                if isinstance(operator, str):
                    if operator.startswith("field_") or "field" in item:
                        coverage.add("field_filter")
                    if operator.startswith("rate_"):
                        coverage.add("rate_operator")
                    if operator.startswith("relative_change") or operator.startswith("relative_drop"):
                        coverage.add("relative_change_or_drop")
                    if operator == "semantic_match":
                        coverage.add("semantic_match")
            if rule.get("debounce"):
                coverage.add("debounce")
            if rule.get("cooldown"):
                coverage.add("cooldown")
            if rule.get("hysteresis"):
                coverage.add("hysteresis")
        if fixture.get("expected_suppressed_events"):
            coverage.add("dedupe_suppression")
        if fixture.get("expected_delivery_reports"):
            coverage.add("delivery_report_output")
        for event in fixture.get("expected_attention_events", []):
            data = event.get("data", {})
            if data.get("evidence") and data.get("privacy"):
                coverage.add("evidence_policy_output")
            if data.get("privacy", {}).get("redaction_report"):
                coverage.add("field_filter")
            for evidence in data.get("evidence", []):
                if evidence.get("kind") == "semantic_score":
                    coverage.add("semantic_match")
        if fixture.get("expected_result") == "capability_mismatch" and compatibility_errors:
            coverage.add("capability_mismatch")
        return coverage

    def _check_declared_coverage(self, fixture: dict[str, Any], coverage: set[str], result: EvaluationResult) -> None:
        declared = set(fixture.get("expected_coverage", []))
        missing = sorted(declared - coverage)
        result.check("expected coverage is derived from contract/transcript/output", not missing, "declared mechanisms have evidence", ", ".join(missing))

    def _check_transcript_alignment(self, fixture: dict[str, Any], result: EvaluationResult) -> None:
        transcript_events = [item.get("data", {}) for item in fixture.get("input_transcript", []) if item.get("kind") == "event"]
        observations = [item.get("data", {}) for item in fixture.get("input_transcript", []) if item.get("kind") == "observation"]
        for state in [item.get("data", {}) for item in fixture.get("input_transcript", []) if item.get("kind") == "state"]:
            for key, value in state.items():
                if "." in key:
                    observations.append({"signal": key, "value": value})
        thread_ids = {item.get("thread_id") for item in transcript_events if item.get("thread_id")}
        mismatches: list[str] = []
        for event in fixture.get("expected_attention_events", []):
            data = event.get("data", {})
            for evidence in data.get("evidence", []):
                value = evidence.get("value")
                if isinstance(value, dict) and value.get("thread_id") and value["thread_id"] not in thread_ids:
                    mismatches.append(f"evidence {evidence.get('evidence_id')} thread_id {value['thread_id']} not in transcript")
                signal = evidence.get("signal")
                if signal:
                    matches = [item for item in observations if item.get("signal") == signal]
                    if not matches:
                        mismatches.append(f"evidence {evidence.get('evidence_id')} signal {signal} not in transcript observations")
                    elif "value" in evidence and not isinstance(evidence.get("value"), dict) and all(item.get("value") != evidence.get("value") for item in matches):
                        mismatches.append(f"evidence {evidence.get('evidence_id')} value {evidence.get('value')!r} not in transcript observations")
                    elif "score" in evidence and all(item.get("score") != evidence.get("score") for item in matches):
                        mismatches.append(f"evidence {evidence.get('evidence_id')} score {evidence.get('score')!r} not in transcript observations")
            email = data.get("payload", {}).get("email", {})
            if email.get("thread_id") and email["thread_id"] not in thread_ids:
                mismatches.append(f"payload email thread_id {email['thread_id']} not in transcript")
        result.check("expected outputs align with input transcript", not mismatches, "event/evidence/payload values come from transcript", "; ".join(mismatches))

    def _check_transcript_order(self, fixture: dict[str, Any], result: EvaluationResult) -> None:
        steps = [item["step"] for item in fixture.get("input_transcript", [])]
        result.check("input transcript is ordered", steps == sorted(steps), "monotonic step order", str(steps))
