# ExAP Package Self-Check Report

Generated at: 2026-05-17T17:28:19.344437+00:00
Total checks: 72
Passed: 72
Failed: 0

## Results

| Check | Result | Detail |
|---|---:|---|
| schema meta exap-attention-contract.schema.json | PASS |  |
| schema meta exap-attention-event.schema.json | PASS |  |
| schema meta exap-capability.schema.json | PASS |  |
| schema meta exap-common.schema.json | PASS |  |
| schema meta exap-lifecycle-message.schema.json | PASS |  |
| schema meta exap-observation.schema.json | PASS |  |
| schema meta exap-profile.schema.json | PASS |  |
| schema meta exap-rule.schema.json | PASS |  |
| canonical refs exap-attention-contract.schema.json | PASS |  |
| canonical refs exap-attention-event.schema.json | PASS |  |
| canonical refs exap-capability.schema.json | PASS |  |
| canonical refs exap-common.schema.json | PASS |  |
| canonical refs exap-lifecycle-message.schema.json | PASS |  |
| canonical refs exap-observation.schema.json | PASS |  |
| canonical refs exap-profile.schema.json | PASS |  |
| canonical refs exap-rule.schema.json | PASS |  |
| valid example 01-process-wait-contract.json | PASS |  |
| valid example 02-gpu-idle-attention-event.json | PASS |  |
| valid example 03-email-important-contract.json | PASS |  |
| valid example 04-mail-attention-event.json | PASS |  |
| valid example 05-provider-capability-process.json | PASS |  |
| valid example 06-provider-capability-mail.json | PASS |  |
| valid example 07-http-contract-create-request.json | PASS |  |
| MCP tools example | PASS |  |
| A2A agent card example | PASS |  |
| profile calendar-focus.exap.json | PASS |  |
| profile ci-cd-monitor.exap.json | PASS |  |
| profile deep-learning-training.exap.json | PASS |  |
| profile email-priority.exap.json | PASS |  |
| profile file-watch.exap.json | PASS |  |
| profile iot-safety.exap.json | PASS |  |
| profile process-monitoring.exap.json | PASS |  |
| profile instantiation fixtures | PASS |  |
| package version binding | PASS |  |
| negative fixture invalid-missing-rules.json | PASS |  |
| negative fixture invalid-unknown-operator.json | PASS |  |
| negative fixture invalid-extra-field.json | PASS |  |
| negative fixture invalid-duplicate-rule-id.json | PASS |  |
| negative fixture invalid-triggered-empty-evidence.json | PASS |  |
| lifecycle wait rejects unknown until | PASS |  |
| lifecycle wait rejects invalid duration | PASS |  |
| lifecycle wait rejects empty time duration | PASS |  |
| lifecycle ack snooze requires snooze_for | PASS |  |
| lifecycle contract.get rejects unknown params | PASS |  |
| lifecycle response rejects arbitrary result | PASS |  |
| lifecycle error accepts JSON-RPC integer code | PASS |  |
| lifecycle response accepts pause result | PASS |  |
| lifecycle error requires exap_code | PASS |  |
| rule rejects exists with value | PASS |  |
| rule rejects rate missing window | PASS |  |
| rule rejects in value not array | PASS |  |
| rule rejects event count missing value | PASS |  |
| rule rejects field filter missing value | PASS |  |
| rule rejects state eq missing value | PASS |  |
| rule rejects state rate missing window | PASS |  |
| rule accepts semantic_match array value | PASS |  |
| rule accepts datetime comparison value | PASS |  |
| rule accepts duration comparison value | PASS |  |
| attention event rejects summary type with triggered status | PASS |  |
| attention event rejects triggered type with suppressed status | PASS |  |
| capability compatibility process example | PASS |  |
| capability compatibility mail example | PASS |  |
| capability self-consistency process | PASS |  |
| capability self-consistency mail | PASS |  |
| capability compatibility rejects signal-level operator | PASS |  |
| YAML reference asyncapi-provider.yaml | PASS |  |
| YAML reference openapi-http-binding.yaml | PASS |  |
| manifest listed files exist | PASS |  |
| normative text has no banned ambiguity terms | PASS |  |
| legacy naming removed | PASS |  |
| schema properties documented | PASS |  |
| all JSON files parse | PASS |  |
