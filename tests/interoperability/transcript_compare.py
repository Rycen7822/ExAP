"""Transcript comparison for C4 interoperability scenarios."""
from __future__ import annotations

from typing import Any

_MISSING = object()


class TranscriptComparator:
    def compare(self, scenario: dict[str, Any], transcripts: list[dict[str, Any]]) -> tuple[bool, list[dict[str, str]]]:
        details: list[dict[str, str]] = []
        assertions = scenario.get("assertions", [])
        for field in assertions:
            values = [self._field_value(transcript, field) for transcript in transcripts]
            missing = any(value is _MISSING for value in values)
            equivalent = not missing and all(value == values[0] for value in values[1:])
            details.append({
                "name": f"{field} equivalent",
                "status": "PASS" if equivalent else "FAIL",
                "expected": "present and equivalent",
                "actual": self._format_values(values),
            })
        for transcript in transcripts:
            has_requests = bool(transcript.get("requests"))
            details.append({"name": f"{transcript['binding']} request transcript present", "status": "PASS" if has_requests else "FAIL", "expected": "non-empty requests", "actual": str(len(transcript.get("requests", [])))})
        passed = all(item["status"] == "PASS" for item in details)
        return passed, details

    def _field_value(self, transcript: dict[str, Any], field: str) -> Any:
        current: Any = transcript
        for part in field.split("."):
            if isinstance(current, list):
                next_items = []
                for item in current:
                    if not isinstance(item, dict) or part not in item:
                        return _MISSING
                    next_items.append(item[part])
                current = next_items
            elif isinstance(current, dict):
                if part not in current:
                    return _MISSING
                current = current[part]
            else:
                return _MISSING
        return current

    def _format_values(self, values: list[Any]) -> str:
        rendered = ["<missing>" if value is _MISSING else repr(value) for value in values]
        return repr(rendered)
