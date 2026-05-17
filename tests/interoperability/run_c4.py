#!/usr/bin/env python3
"""Run ExAP C4 interoperability scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import importlib
import json
import subprocess
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tests.interoperability.transcript_compare import TranscriptComparator
else:
    from .transcript_compare import TranscriptComparator

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = {
    "http": "tests.interoperability.binding_adapters.http_adapter:HttpTranscriptAdapter",
    "mcp": "tests.interoperability.binding_adapters.mcp_adapter:McpTranscriptAdapter",
    "a2a": "tests.interoperability.binding_adapters.a2a_adapter:A2aTranscriptAdapter",
    "local": "tests.interoperability.binding_adapters.local_adapter:LocalTranscriptAdapter",
}


@dataclass
class ScenarioResult:
    scenario_id: str
    name: str
    path: Path
    bindings: list[str]
    passed: bool
    details: list[dict[str, str]]
    transcripts: list[dict[str, Any]]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def load_adapter(binding: str) -> Any:
    module_name, _, class_name = ADAPTERS[binding].partition(":")
    module = importlib.import_module(module_name)
    return getattr(module, class_name)()


def compact(value: Any, limit: int = 700) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= limit else text[:limit] + "..."


def collect_scenarios(path: Path) -> list[Path]:
    return sorted(item for item in path.glob("*.json") if item.is_file())


def run_scenario(path: Path, comparator: TranscriptComparator) -> ScenarioResult:
    scenario = json.loads(path.read_text(encoding="utf-8"))
    transcripts = [load_adapter(binding).run(scenario) for binding in scenario["bindings"]]
    passed, details = comparator.compare(scenario, transcripts)
    return ScenarioResult(scenario["scenario_id"], scenario.get("name", path.stem), path, scenario["bindings"], passed, details, transcripts)


def comparator_missing_field_guard(comparator: TranscriptComparator) -> bool:
    passed, _ = comparator.compare({"assertions": ["event.missing_leaf"]}, [
        {"binding": "probe-a", "requests": [{"ok": True}], "event": {}},
        {"binding": "probe-b", "requests": [{"ok": True}], "event": {}},
    ])
    return not passed


def write_report(path: Path, scenario_root: Path, results: list[ScenarioResult], comparator_guard_passed: bool) -> None:
    passed = sum(1 for result in results if result.passed)
    binding_pairs = sorted({"+".join(result.bindings) for result in results})
    lines = [
        "# ExAP C4 Interoperability Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Level: C4",
        f"Git commit: `{git_commit()}`",
        "ExAP version: `0.2.0-draft`",
        f"Scenarios: `{scenario_root.as_posix()}`",
        f"Binding matrix: {', '.join(binding_pairs)}",
        f"Summary: {passed}/{len(results)} scenarios PASS; comparator guard {'PASS' if comparator_guard_passed else 'FAIL'}",
        "",
        "| Scenario | Bindings | Status | Check count |",
        "|---|---|---:|---:|",
    ]
    for result in results:
        lines.append(f"| {result.scenario_id} {result.name} | {'+'.join(result.bindings)} | {'PASS' if result.passed else 'FAIL'} | {len(result.details)} |")
    lines.extend(["", "## Details", ""])
    for result in results:
        lines.append(f"### {result.scenario_id}. {result.name}")
        lines.append("")
        lines.append(f"Path: `{result.path.relative_to(ROOT).as_posix()}`")
        lines.append(f"Bindings: {', '.join(result.bindings)}")
        lines.append(f"Status: {'PASS' if result.passed else 'FAIL'}")
        lines.append("")
        lines.append("| Check | Status | Expected | Actual |")
        lines.append("|---|---:|---|---|")
        for detail in result.details:
            lines.append(f"| {detail['name']} | {detail['status']} | {detail['expected'].replace('|', '/')} | {detail['actual'].replace('|', '/')[:900]} |")
        lines.append("")
        lines.append("#### Normalized transcripts")
        lines.append("")
        for transcript in result.transcripts:
            summary = {k: transcript.get(k) for k in ["binding", "version", "profile", "transport", "delivery_mode", "content_mode", "contract_id", "attention_id", "return_reason", "status", "ack_status", "stream_id", "frame_types", "push_success", "errors", "state_transitions", "event"] if k in transcript}
            lines.append(f"- `{transcript['binding']}`: `{compact(summary)}`")
        lines.append("")
    lines.extend([
        "## Rerun",
        "",
        "```bash",
        f"python tests/interoperability/run_c4.py --scenarios {scenario_root.relative_to(ROOT).as_posix()} --report {path.as_posix()}",
        "```",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ExAP C4 interoperability scenarios")
    parser.add_argument("--scenarios", default="tests/interoperability/scenarios")
    parser.add_argument("--report", default="tests/interoperability/reports/c4-report.md")
    args = parser.parse_args()
    scenario_root = Path(args.scenarios)
    if not scenario_root.is_absolute():
        scenario_root = ROOT / scenario_root
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    comparator = TranscriptComparator()
    results = [run_scenario(path, comparator) for path in collect_scenarios(scenario_root)]
    comparator_guard_passed = comparator_missing_field_guard(comparator)
    write_report(report_path, scenario_root, results, comparator_guard_passed)
    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.scenario_id} {result.name}")
        for detail in result.details:
            if detail["status"] != "PASS":
                print(f"  - {detail['name']}: expected {detail['expected']}; actual {detail['actual']}")
    if not comparator_guard_passed:
        print("[FAIL] comparator missing-field guard")
    failed = [result for result in results if not result.passed]
    print(f"C4 Interoperability: {len(results) - len(failed)}/{len(results)} scenarios PASS; comparator guard {'PASS' if comparator_guard_passed else 'FAIL'}")
    print(f"Report: {report_path}")
    return 1 if failed or not comparator_guard_passed else 0


if __name__ == "__main__":
    raise SystemExit(main())
