# EAP Package Audit Notes

This working document records facts observed while reading the existing package, inconsistencies found, and fixes applied before creating the revised archive.


## Initial structural inspection

- Source archive: `/mnt/data/eap_spec_package.zip`.
- Extracted files: 50.
- Existing Markdown documents: top-level docs plus `docs/00` through `docs/16`.
- Existing schemas: attention contract, attention event, capability, common, observation, profile, rule.
- Existing examples/profiles are syntactically valid JSON.

## Initial schema issue

Validation using `jsonschema` encountered a cross-reference resolution failure involving relative `$ref` values such as `eap-rule.schema.json` and local references. The practical fix is to use absolute canonical schema IDs for inter-schema references. Local references remain `#/$defs/...` only inside the same document.

## External protocol alignment facts to incorporate

- MCP uses JSON-RPC 2.0, stateful connections, client/server capability negotiation, server primitives (`tools`, `resources`, `prompts`), client primitives (`sampling`, `roots`, `elicitation`), and utilities including progress, cancellation, error reporting, logging.
- MCP architecture distinguishes hosts, clients, and servers; data layer and transport layer; transports include stdio and streamable HTTP.
- A2A is agent-to-agent, task-oriented, supports Agent Cards, Tasks, Messages, Parts, Artifacts, SSE streaming, push notifications, and opaque execution.
- EAP must define itself as environment-to-consumer awareness contracts and provide bindings to MCP and A2A rather than replacing either protocol.

## Final Revision Summary

This final revision rebuilds EAP as a general environment awareness protocol rather than a coding-agent-only runtime. The package includes normative Markdown specifications, JSON Schemas, example contracts and events, domain profiles, reference API descriptions, and executable conformance tests.

Resolved issues:

- Replaced ambiguous relative cross-schema references with canonical schema IDs under `https://eap.dev/schemas/`.
- Added method-specific validation for lifecycle JSON-RPC messages.
- Added explicit MCP and A2A binding guidance while keeping EAP Core transport-neutral.
- Added A2A Agent Card and MCP tools examples.
- Added negative conformance fixtures that verify invalid contracts, events, capabilities, lifecycle requests, and profiles fail validation.
- Added documentation coverage checks for schema properties.
- Added manifest checks, YAML reference checks, canonical reference checks, and banned ambiguity term checks.

Final test command:

```bash
python3 tests/conformance.py
```

Final expected result:

```text
All conformance checks passed.
```
