# Revision Draft Plan

## Goals

1. Convert ExAP from a coding-agent runtime concept into a general environment awareness protocol.
2. Define unambiguous core objects, parameters, lifecycle states, delivery actions, and rule semantics.
3. Align the agent binding with current MCP and A2A development patterns without making ExAP depend on either protocol.
4. Replace ambiguous relative schema references with canonical absolute `$id` references.
5. Add executable conformance tests that validate schemas, examples, profiles, negative cases, document manifests, and cross-document terminology.

## File strategy

- Keep the package structure stable so existing readers can find the old topics.
- Add one dedicated MCP/A2A integration document.
- Add `tests/conformance.py`, `tests/conformance-report.md`, and negative fixtures.
- Use ExAP version `0.2.0-draft` throughout the package.

## Final acceptance checks

- No JSON parse errors.
- No YAML parse errors in reference files.
- All schemas pass Draft 2020-12 meta-schema validation.
- All external `$ref` values resolve through canonical schema IDs.
- All examples and profiles validate against the proper schemas.
- Negative fixtures fail for the expected reasons.
- No obsolete version references remain outside audit context.
- Event rule data uses `data.rule`.
