"""Compatibility checks used by the smoke-grade reference rule engine."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class RuleEngine:
    def compatibility_errors(self, contract: dict[str, Any], capability: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        signal_specs = {item.get("name"): item for item in capability.get("signals", []) if isinstance(item, dict)}
        supported_signals = set(signal_specs)
        supported_events = {item.get("event_type") for item in capability.get("event_types", [])}
        operators = set(capability.get("rule_capabilities", {}).get("operators", []))
        signal_operators = {name: set(spec.get("operators", [])) for name, spec in signal_specs.items()}

        scope = contract.get("scope", {})
        scope_signals = set(scope.get("signals", []))
        scope_events = set(scope.get("events", []))
        for signal in sorted(scope_signals):
            if signal not in supported_signals:
                errors.append(f"scope signal not in capability {signal}")
        for event_type in sorted(scope_events):
            if event_type not in supported_events:
                errors.append(f"scope event not in capability {event_type}")

        rule_ids = [rule.get("rule_id") for rule in contract.get("rules", [])]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("duplicate rule_id")

        for rule in contract.get("rules", []):
            rule_id = rule.get("rule_id")
            signals, events = self._rule_refs(rule)
            for signal in sorted(signals - scope_signals):
                errors.append(f"rule {rule_id} signal outside scope {signal}")
            for event_type in sorted(events - scope_events):
                errors.append(f"rule {rule_id} event outside scope {event_type}")
            for signal in sorted(signals - supported_signals):
                errors.append(f"rule {rule_id} signal not in capability {signal}")
            for event_type in sorted(events - supported_events):
                errors.append(f"rule {rule_id} event not in capability {event_type}")
            for operator in sorted(self._condition_operators(rule.get("condition", {})) - operators):
                errors.append(f"rule {rule_id} operator not in capability {operator}")
            for condition in self._iter_conditions(rule.get("condition", {})):
                if condition.get("type") == "signal":
                    signal = condition.get("signal")
                    operator = condition.get("operator")
                    if signal in signal_operators and signal_operators[signal] and operator not in signal_operators[signal]:
                        errors.append(f"rule {rule_id} operator {operator} not allowed for signal {signal}")
        return errors

    def _iter_conditions(self, condition: dict[str, Any]) -> Iterable[dict[str, Any]]:
        if not isinstance(condition, dict):
            return
        yield condition
        condition_type = condition.get("type")
        if condition_type in {"all", "any"}:
            for child in condition.get("conditions", []):
                yield from self._iter_conditions(child)
        elif condition_type == "not":
            yield from self._iter_conditions(condition.get("condition", {}))
        elif condition_type == "correlation":
            for child in condition.get("conditions", []):
                yield from self._iter_conditions(child.get("condition", {}))

    def _rule_refs(self, rule: dict[str, Any]) -> tuple[set[str], set[str]]:
        signals: set[str] = set()
        events: set[str] = set()
        for condition in self._iter_conditions(rule.get("condition", {})):
            if condition.get("type") == "signal" and condition.get("signal"):
                signals.add(condition["signal"])
            if condition.get("type") == "event" and condition.get("event_type"):
                events.add(condition["event_type"])
            if condition.get("type") == "state" and condition.get("signal"):
                signals.add(condition["signal"])
        if isinstance(rule.get("hysteresis"), dict):
            for condition in self._iter_conditions(rule["hysteresis"].get("recover_when", {})):
                if condition.get("type") == "signal" and condition.get("signal"):
                    signals.add(condition["signal"])
                if condition.get("type") == "event" and condition.get("event_type"):
                    events.add(condition["event_type"])
        return signals, events

    def _condition_operators(self, condition: dict[str, Any]) -> set[str]:
        operators: set[str] = set()
        for item in self._iter_conditions(condition):
            operator = item.get("operator")
            if isinstance(operator, str):
                operators.add(operator)
        return operators
