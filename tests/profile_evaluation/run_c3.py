#!/usr/bin/env python3
"""Run ExAP C3 profile evaluation transcript checks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import json
import subprocess
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tests.profile_evaluation.evaluator_adapter import ProfileTranscriptEvaluator
else:
    from .evaluator_adapter import ProfileTranscriptEvaluator

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_COVERAGE = {
    "signal_condition",
    "event_condition",
    "field_filter",
    "semantic_match",
    "debounce",
    "cooldown",
    "hysteresis",
    "dedupe_suppression",
    "evidence_policy_output",
    "delivery_report_output",
    "capability_mismatch",
}


@dataclass
class SuiteResult:
    case_id: str
    name: str
    path: Path
    passed: bool
    details: list[dict[str, str]]
    coverage: set[str]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def collect_fixture_paths(fixtures: Path) -> list[Path]:
    return sorted(path for path in fixtures.rglob("*.json") if path.is_file())


def write_report(path: Path, fixture_root: Path, results: list[SuiteResult], coverage: set[str]) -> None:
    passed = sum(1 for result in results if result.passed)
    coverage_pass = REQUIRED_COVERAGE <= coverage
    lines = [
        "# ExAP C3 Profile Evaluation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Level: C3",
        f"Git commit: `{git_commit()}`",
        "ExAP version: `0.2.0-draft`",
        f"Fixtures: `{fixture_root.as_posix()}`",
        f"Summary: {passed}/{len(results)} transcripts PASS; coverage {'PASS' if coverage_pass else 'FAIL'}",
        "",
        "| Transcript | Status | Step count |",
        "|---|---:|---:|",
    ]
    for result in results:
        rel = result.path.relative_to(ROOT)
        lines.append(f"| {result.case_id} `{rel.as_posix()}` | {'PASS' if result.passed else 'FAIL'} | {len(result.details)} |")
    lines.extend(["", "## Coverage", ""])
    lines.append("| Mechanism | Status |")
    lines.append("|---|---:|")
    for item in sorted(REQUIRED_COVERAGE):
        lines.append(f"| {item} | {'PASS' if item in coverage else 'FAIL'} |")
    lines.extend(["", "## Transcript Details", ""])
    for result in results:
        lines.append(f"### {result.case_id}. {result.name}")
        lines.append("")
        lines.append(f"Path: `{result.path.relative_to(ROOT).as_posix()}`")
        lines.append(f"Status: {'PASS' if result.passed else 'FAIL'}")
        lines.append(f"Coverage: {', '.join(sorted(result.coverage))}")
        lines.append("")
        lines.append("| Check | Status | Expected | Actual |")
        lines.append("|---|---:|---|---|")
        for detail in result.details:
            lines.append(f"| {detail['name']} | {detail['status']} | {detail['expected'].replace('|', '/')} | {detail['actual'].replace('|', '/')[:900]} |")
        lines.append("")
    lines.extend([
        "## Rerun",
        "",
        "```bash",
        f"python tests/profile_evaluation/run_c3.py --fixtures {fixture_root.relative_to(ROOT).as_posix()} --report {path.as_posix()}",
        "```",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ExAP C3 profile evaluation transcripts")
    parser.add_argument("--fixtures", default="tests/fixtures/profile-transcripts")
    parser.add_argument("--report", default="tests/profile_evaluation/reports/c3-report.md")
    args = parser.parse_args()
    fixture_root = Path(args.fixtures)
    if not fixture_root.is_absolute():
        fixture_root = ROOT / fixture_root
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    evaluator = ProfileTranscriptEvaluator()
    results = []
    coverage: set[str] = set()
    for fixture_path in collect_fixture_paths(fixture_root):
        evaluated = evaluator.evaluate_file(fixture_path)
        coverage.update(evaluated.coverage)
        results.append(SuiteResult(evaluated.case_id, evaluated.name, fixture_path, evaluated.passed, evaluated.details, evaluated.coverage))
    coverage_pass = REQUIRED_COVERAGE <= coverage
    write_report(report_path, fixture_root, results, coverage)
    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.case_id} {result.name}")
        for detail in result.details:
            if detail["status"] != "PASS":
                print(f"  - {detail['name']}: expected {detail['expected']}; actual {detail['actual']}")
    if not coverage_pass:
        print(f"[FAIL] coverage missing: {', '.join(sorted(REQUIRED_COVERAGE - coverage))}")
    failed = [result for result in results if not result.passed]
    print(f"C3 Profile Evaluation: {len(results) - len(failed)}/{len(results)} transcripts PASS; coverage {'PASS' if coverage_pass else 'FAIL'}")
    print(f"Report: {report_path}")
    return 1 if failed or not coverage_pass else 0


if __name__ == "__main__":
    raise SystemExit(main())
