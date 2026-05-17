<div align="center">

# ExAP

**External Awareness Protocol: a verifiable attention contract for external-world awareness across agents, applications, services, daemons, brokers, and runtimes.**

Declare who cares about what, when it becomes worth attention, what evidence is carried, how it is delivered, and how privacy is enforced.

</div>

<br/>

<p align="center">
  <a href="VERSION.md"><img src="https://img.shields.io/badge/Version-0.2.0--draft-f5c542?style=for-the-badge" alt="Version: 0.2.0-draft"></a>
  <a href="docs/00-index.md"><img src="https://img.shields.io/badge/Docs-18%20chapters-0969da?style=for-the-badge" alt="Documentation: 18 chapters"></a>
  <a href="schemas"><img src="https://img.shields.io/badge/JSON%20Schema-2020--12-2ea44f?style=for-the-badge" alt="JSON Schema Draft 2020-12"></a>
  <a href="examples"><img src="https://img.shields.io/badge/Examples-contracts%20%7C%20events%20%7C%20bindings-5865F2?style=for-the-badge" alt="Examples"></a>
  <a href="tests/conformance.py"><img src="https://img.shields.io/badge/Package%20Check-72%2F72%20PASS-blue?style=for-the-badge" alt="Package Check: 72 of 72 passed"></a>
  <a href="docs/17-mcp-a2a-integration.md"><img src="https://img.shields.io/badge/Agent%20Bindings-MCP%20%7C%20A2A-ff69b4?style=for-the-badge" alt="Agent bindings: MCP and A2A"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.zh-CN.md">简体中文</a>
</p>

> ExAP is the External Awareness Protocol specification package.
> It is built for agents, applications, services, daemons, brokers, and runtimes that need external-world awareness without fixed-interval polling.
> A Consumer creates an Attention Contract; a Provider observes only the declared scope, evaluates the declared rules, and returns an Attention Event with evidence, delivery metadata, and a privacy report.

---

## What ExAP is

ExAP is the External Awareness Protocol specification package. It defines a general contract layer for turning “tell me when this external condition deserves attention” into structured, validated, auditable protocol objects.

ExAP is about the attention boundary between agents, applications, services, automation systems, and the outside world: which objects can be observed, which signals can be used, which conditions deserve attention, how events are delivered, how much evidence can be carried, and how privacy plus authorization are enforced.

It answers five questions:

1. Which Environment and Subjects a Consumer cares about.
2. Which Signals and Events a Provider can observe.
3. How the Rule DSL decides that something is worth attention.
4. How an Attention Event carries reason, evidence, severity, delivery action, and acknowledgement requirements.
5. How PrivacyPolicy constrains authorization, field-level redaction, data minimization, retention, audit, and agent memory.

ExAP currently ships the protocol specification, JSON Schemas, examples, domain profiles, binding references, and conformance tests. The current package focuses on the protocol surface; `docs/14-reference-implementation.md` defines the reference implementation boundaries for `exapd`, `exapctl`, `exap-mcp-server`, and `exap-a2a-agent`.

## Why ExAP exists

Many agents and automation systems wait for external change by fixed-interval polling: a process exits, a GPU becomes idle, an email arrives, CI fails, a file appears, a calendar event starts, an IoT alarm fires, or a remote task finishes. Polling adds latency, noise, token and bandwidth cost, unclear privacy boundaries, and weak auditability.

ExAP turns that waiting pattern into an explicit contract:

```text
Consumer declares attention intent
        ↓
Provider publishes capability and validates the contract
        ↓
Provider observes subjects, signals, and events inside the declared scope
        ↓
Rule DSL evaluates whether the condition is satisfied
        ↓
Provider delivers Attention Event, Evidence, PrivacyReport, DeliveryReport
        ↓
Consumer acknowledges, snoozes, dismisses, escalates, or revokes
```

This changes external awareness from “keep asking what happened” into “deliver a constrained event only when the declared condition is satisfied”.

## Standards and bindings

ExAP defines the attention-contract layer and maps cleanly onto common event, telemetry, transport, security, and agent protocols:

| Category | ExAP integration role |
|---|---|
| CloudEvents | ExAP Attention Event uses a CloudEvents-compatible envelope while adding attention-specific reason, evidence, privacy report, and delivery report fields. |
| AsyncAPI / OpenAPI | AsyncAPI and OpenAPI describe ExAP message channels, HTTP bindings, lifecycle requests, and event streams. |
| OpenTelemetry | Metrics, logs, and traces can feed ExAP Observation, Event, or Evidence records. |
| MQTT / NATS / Kafka / Webhook | These transports can carry ExAP delivery modes; ExAP supplies contract, rule, delivery, and acknowledgement semantics. |
| OAuth / mTLS / API key / IAM | Existing security systems provide identity and authorization; ExAP binds scope, consent, redaction, retention, and audit to each contract. |
| MCP | MCP exposes ExAP Lifecycle API as tools and publishes capability, active contracts, recent attention, and profiles as resources. |
| A2A | A2A maps create-contract and wait flows to tasks, with `application/exap+json` Attention Events returned as artifacts. |

## What this package contains

| Surface | Content |
|---|---|
| Protocol version | `0.2.0-draft`. |
| Normative docs | `docs/00-index.md` through `docs/17-mcp-a2a-integration.md`, covering core model, Contract, Rule DSL, Event, Capability, Lifecycle, Transport, Privacy, Profiles, Conformance, MCP, and A2A. |
| JSON Schemas | 8 Draft 2020-12 schemas with canonical `$id` values under `https://exap.dev/schemas/0.2.0-draft/`. |
| Examples | Contracts, Attention Events, Capability Documents, Lifecycle requests, MCP tools, A2A Agent Card, and local CLI examples. |
| Domain Profiles | Process monitoring, deep learning training, email priority, calendar focus, file watch, IoT safety, and CI/CD monitoring. |
| References | Draft OpenAPI for the HTTP binding, draft AsyncAPI for provider event streams, and smoke-grade Python reference implementation modules under `reference/`. |
| Package Check | `tests/conformance.py` is the C0/C1 package self-check for schemas, references, examples, profiles, negative fixtures, capability compatibility, YAML references, manifest entries, and documentation coverage. |
| Runtime Suites | C2 provider behavior, C3 profile transcript evaluation, C4 binding interoperability, and R4 reference smoke suites generate Markdown reports under `tests/**/reports/` and `reference/smoke/reports/`. |

## Core objects

| Object | Role |
|---|---|
| Environment | Boundary where external awareness happens: a machine, workspace, project, home space, enterprise tenant, or cloud environment. |
| Subject | Observed object: mailbox, process, gpu, file, calendar, pipeline, iot_device, agent_task. |
| Signal | Observable state, metric, or property on a Subject, such as `process.cpu.percent`, `gpu.util.percent`, or `mail.message.received`. |
| Observation | Raw observation of a Signal at a point in time. |
| Event | Discrete event from a system API, SaaS webhook, log, queue, or sensor. |
| Capability Document | Machine-readable Provider declaration for ExAP versions, Subjects, Signals, Events, Rules, Delivery, Privacy, limits, and bindings. |
| Attention Contract | Consumer-submitted contract containing intent, scope, rules, delivery, privacy, lifecycle, memory, and integrations. |
| Rule DSL | Structured JSON condition language with boolean, signal, event, state, correlation, window aggregate, debounce, cooldown, and hysteresis support. |
| Attention Event | Structured event delivered after a Rule match, carrying reason, severity, rule reference, evidence, payload, privacy report, and delivery report. |
| PrivacyPolicy / PrivacyReport | Declaration and report for data minimization, field-level redaction, forbidden fields, retention, audit, and consent. |

## Minimal reading path

| Order | File | What it gives you |
|---:|---|---|
| 1 | `docs/01-overview-and-scope.md` | Goals, standards and binding roles, roles, and workflow. |
| 2 | `docs/02-core-model.md` | Environment, Subject, Signal, Observation, Event, Contract, Attention Event. |
| 3 | `docs/03-attention-contract.md` | How a Consumer expresses intent, scope, rules, delivery, privacy, and memory policy. |
| 4 | `docs/04-rule-dsl.md` | Conditions, operators, aggregates, debounce, cooldown, hysteresis, and missing-value semantics. |
| 5 | `docs/05-attention-event.md` | CloudEvents-compatible Attention Event, Evidence, PrivacyReport, and DeliveryReport. |
| 6 | `docs/06-capability-discovery.md` | How a Provider declares capability and how a Consumer discovers before creating a Contract. |
| 7 | `docs/07-lifecycle-api.md` | `exap.discover`, `exap.contract.create`, `exap.wait`, `exap.status`, `exap.attention.ack`, `exap.contract.revoke`. |
| 8 | `docs/09-privacy-security.md` | Authorization, consent, redaction, retention, audit, secret handling, and agent action safety. |
| 9 | `docs/16-standards-compatibility.md` | Relationship with CloudEvents, AsyncAPI, OpenTelemetry, MQTT, NATS, OAuth, MCP, and A2A. |
| 10 | `docs/17-mcp-a2a-integration.md` | How ExAP maps to MCP tools/resources and A2A tasks/artifacts. |

See `docs/00-index.md` for the full manual and `MANIFEST.md` for the complete file map.

## Quick validation

```bash
cd /path/to/ExAP
python -m pip install jsonschema referencing PyYAML
python tests/conformance.py
```

The current conformance report lives at `tests/conformance-report.md`. The suite covers:

- schema meta-validation;
- canonical `$ref` resolution;
- valid examples;
- MCP tools and A2A Agent Card examples;
- 7 domain profiles;
- negative fixtures;
- OpenAPI / AsyncAPI YAML;
- manifest file existence;
- legacy-version and ambiguous-requirement wording checks;
- schema property documentation coverage;
- JSON parsing for all JSON files.

## Provider implementation path

A Provider observes the external environment, evaluates rules, and delivers events. A Provider-Minimal implementation covers:

1. Publish a capability document listing supported ExAP versions, subject types, signals, event types, operators, aggregates, delivery modes, privacy capabilities, limits, and bindings.
2. Accept `exap.contract.create` and validate the Contract with the attention contract schema under `schemas/`.
3. Validate ExAP version, scope authorization, Subject resolution, Signal/Event support, Rule DSL capability, delivery mode, privacy policy, and rule ID uniqueness.
4. Collect Observations or Events in the background, then evaluate Rule DSL with three-valued logic, window aggregate, debounce, cooldown, hysteresis, and dedupe.
5. Generate `exap.attention.triggered`, `exap.attention.recovered`, `exap.attention.summary`, or state change events.
6. Apply forbidden-field checks, redaction, payload limits, retention, and audit before delivery.
7. Support `exap.wait`, `exap.attention.ack`, and `exap.contract.revoke`.

See `templates/provider-checklist.md` for the Provider checklist.

## Consumer and agent integration path

A Consumer creates Contracts and receives Attention Events. A Consumer-Minimal or Consumer-Agent integration covers:

1. Call `exap.discover` and read Provider capability.
2. Select a Provider-supported ExAP version and create a Contract that fits capability, authorization, and privacy limits.
3. Receive results through `blocking_wait`, `stream`, `push`, or `pull_with_state_compression`.
4. Validate Attention Event schema, treat payload as untrusted input, and rely on evidence plus privacy report for usable context.
5. Execute `exap.attention.ack` for events with `requires_ack=true`.
6. Execute `exap.contract.revoke` when the attention need is over.
7. Respect the Contract `memory` policy; when `memory.allowed=false`, keep payload, evidence, and summary within short-lived processing, with long-term memory limited to policy-approved information.

See `templates/consumer-checklist.md` for the Consumer checklist.

## Agent bindings

ExAP defines explicit binding points for mainstream agent protocols:

| Binding | Mapping |
|---|---|
| MCP | ExAP Provider acts as an MCP server and exposes `exap_discover`, `exap_contract_create`, `exap_wait`, `exap_status`, `exap_attention_ack`, and `exap_contract_revoke` tools; capability, active contracts, recent attention, and profiles can be resources. |
| A2A | ExAP Provider acts as a remote agent and declares create-contract plus wait skills in its Agent Card; Contract creation and wait map to Tasks, and Attention Events are returned as `application/exap+json` Artifacts. |

This keeps MCP tool/resource semantics and A2A task lifecycle intact while ExAP focuses on external-to-consumer awareness semantics.

## Scenario coverage

ExAP spans coding agents, automation systems, local machines, SaaS surfaces, and physical environments. These objects can be Subjects or part of an Environment:

- email, threads, contacts, and inboxes;
- local processes, process groups, logs, and jobs;
- GPUs, disks, hardware, and system resources;
- files, directories, and artifacts;
- calendars, meetings, and focus windows;
- IoT devices, sensors, and gateways;
- CI/CD pipelines, builds, deployments, and releases;
- cloud resources, queues, databases, tickets, and pull requests;
- agent tasks, remote agents, workspaces, and generated artifacts.

## Version and compatibility

Current version: `0.2.0-draft`.

Version rules live in `VERSION.md`: Providers list supported versions in capability document `exap_versions`; Consumers select one before Contract creation; Providers reject unknown MAJOR versions; schema `$id` values stay unique within a release package.
