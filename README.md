<div align="center">

# ExAP

**Environment Awareness Protocol：用一个可验证的关注契约，声明谁关心什么、何时提醒、携带哪些证据、如何交付、如何保护隐私。**

**A contract layer for environment awareness: declare who cares about what, when it becomes worth attention, what evidence is carried, how it is delivered, and how privacy is enforced.**

</div>

<br/>

<p align="center">
  <a href="VERSION.md"><img src="https://img.shields.io/badge/Version-0.2.0--draft-f5c542?style=for-the-badge" alt="Version: 0.2.0-draft"></a>
  <a href="docs/00-index.md"><img src="https://img.shields.io/badge/Docs-18%20chapters-0969da?style=for-the-badge" alt="Documentation: 18 chapters"></a>
  <a href="schemas"><img src="https://img.shields.io/badge/JSON%20Schema-2020--12-2ea44f?style=for-the-badge" alt="JSON Schema Draft 2020-12"></a>
  <a href="examples"><img src="https://img.shields.io/badge/Examples-contracts%20%7C%20events%20%7C%20bindings-5865F2?style=for-the-badge" alt="Examples"></a>
  <a href="tests/conformance.py"><img src="https://img.shields.io/badge/Conformance-43%2F43%20PASS-blue?style=for-the-badge" alt="Conformance: 43 of 43 passed"></a>
  <a href="docs/17-mcp-a2a-integration.md"><img src="https://img.shields.io/badge/Agent%20Bindings-MCP%20%7C%20A2A-ff69b4?style=for-the-badge" alt="Agent bindings: MCP and A2A"></a>
</p>

> ExAP is the specification package for EAP, the Environment Awareness Protocol.
> It is built for agents, applications, services, daemons, brokers, and runtimes that need background awareness without fixed-interval polling.
> A Consumer creates an Attention Contract; a Provider observes only the declared scope, evaluates the declared rules, and returns an Attention Event with evidence, delivery metadata, and a privacy report.

---

## 中文版

### ExAP 是什么

ExAP 是 EAP（Environment Awareness Protocol）的规范包。EAP 定义一种通用的“环境感知契约”层，用来把“如果某个环境条件变得值得关注，请通知我”表达成结构化、可校验、可审计的协议对象。

它回答五个问题：

1. Consumer 关心哪个 Environment 与哪些 Subject。
2. Provider 能观察哪些 Signal 与 Event。
3. Rule DSL 如何判断“值得注意”。
4. Attention Event 如何携带原因、证据、严重级别、交付动作和确认要求。
5. PrivacyPolicy 如何约束授权、字段级脱敏、数据最小化、保留期、审计和 agent memory。

ExAP 当前交付的是协议规范、JSON Schema、示例、领域 Profile、绑定参考和一致性测试。它不是一个已经打包的运行时守护进程；`docs/14-reference-implementation.md` 固定了未来参考实现的组件边界，包括 `eapd`、`eapctl`、`eap-mcp-server` 和 `eap-a2a-agent`。

### 为什么需要 EAP

许多 agent 和自动化系统会用固定间隔轮询来等待外部世界变化：进程结束、GPU 空闲、邮件到达、CI 失败、文件出现、日历开始、IoT 告警、远程任务完成。轮询会带来延迟、噪声、token/带宽浪费、隐私边界模糊和审计困难。

EAP 把这种等待改成显式契约：

```text
Consumer 声明关注意图
        ↓
Provider 发布 capability 并校验 contract
        ↓
Provider 在后台观察 scope 内的 subject、signal、event
        ↓
Rule DSL 判断条件是否满足
        ↓
Provider 交付 Attention Event、Evidence、PrivacyReport、DeliveryReport
        ↓
Consumer ack、snooze、dismiss、escalate 或 revoke
```

### EAP 不替代什么

EAP 位于现有系统之上，不取代它们：

| 类别 | EAP 的边界 |
|---|---|
| CloudEvents | EAP Attention Event 使用 CloudEvents-compatible envelope，但 CloudEvents 仍负责通用事件 envelope。 |
| AsyncAPI / OpenAPI | EAP 可用它们描述接口和 message channel，但不取代 API 描述标准。 |
| OpenTelemetry | EAP 可消费 metrics、logs、traces 作为 Observation、Event 或 Evidence，但不取代遥测采集。 |
| MQTT / NATS / Kafka / Webhook | EAP 定义交付语义，底层传输仍由这些系统负责。 |
| OAuth / mTLS / API key / IAM | EAP 绑定 scope、consent、redaction、retention、audit，但认证授权仍由现有安全系统执行。 |
| MCP | MCP 负责 agent-to-tool/resource；EAP 通过 MCP tools 暴露 Lifecycle API。 |
| A2A | A2A 负责 agent-to-agent task；EAP 通过 A2A artifact 传递 `application/eap+json` Attention Event。 |

### 当前包内容

| Surface | 内容 |
|---|---|
| Protocol version | `0.2.0-draft`。 |
| Normative docs | `docs/00-index.md` 到 `docs/17-mcp-a2a-integration.md`，覆盖核心模型、Contract、Rule DSL、Event、Capability、Lifecycle、Transport、Privacy、Profiles、Conformance、MCP、A2A。 |
| JSON Schemas | 8 个 Draft 2020-12 schema，canonical `$id` 位于 `https://eap.dev/schemas/`。 |
| Examples | Contract、Attention Event、Capability Document、Lifecycle request、MCP tools、A2A Agent Card、local CLI 样例。 |
| Domain Profiles | process monitoring、deep learning training、email priority、calendar focus、file watch、IoT safety、CI/CD monitoring。 |
| References | HTTP binding 的 OpenAPI 草案与 provider event stream 的 AsyncAPI 草案。 |
| Conformance | `tests/conformance.py` 执行 schema、引用、示例、profile、负面用例、YAML、清单和文档覆盖检查。 |

### 核心对象

| 对象 | 作用 |
|---|---|
| Environment | 感知发生的边界，例如机器、工作区、项目、家庭空间、企业租户或云环境。 |
| Subject | 被观察对象，例如 mailbox、process、gpu、file、calendar、pipeline、iot_device、agent_task。 |
| Signal | Subject 上可观察的状态、指标或属性，例如 `process.cpu.percent`、`gpu.util.percent`、`mail.message.received`。 |
| Observation | 对某个 Signal 在某一时刻的原始观测。 |
| Event | 离散事件，可来自系统 API、SaaS webhook、日志、队列或传感器。 |
| Capability Document | Provider 对 EAP 版本、Subject、Signal、Event、Rule、Delivery、Privacy、limits、bindings 的机器可读声明。 |
| Attention Contract | Consumer 提交给 Provider 的关注契约，包含 intent、scope、rules、delivery、privacy、lifecycle、memory 和 integrations。 |
| Rule DSL | 用结构化 JSON 表达条件，支持 boolean、signal、event、state、correlation、window aggregate、debounce、cooldown、hysteresis。 |
| Attention Event | Rule 触发后交付给 Consumer 的结构化事件，包含 reason、severity、rule reference、evidence、payload、privacy report、delivery report。 |
| PrivacyPolicy / PrivacyReport | 声明和报告数据最小化、字段级脱敏、禁止字段、保留期、审计和 consent。 |

### 最小阅读路径

| 顺序 | 文件 | 读完后能理解什么 |
|---:|---|---|
| 1 | `docs/01-overview-and-scope.md` | EAP 的目标、非目标、角色和工作流。 |
| 2 | `docs/02-core-model.md` | Environment、Subject、Signal、Observation、Event、Contract、Attention Event。 |
| 3 | `docs/03-attention-contract.md` | Consumer 如何表达 intent、scope、rules、delivery、privacy 和 memory policy。 |
| 4 | `docs/04-rule-dsl.md` | Rule 条件、operator、aggregate、debounce、cooldown、hysteresis 和缺失值语义。 |
| 5 | `docs/05-attention-event.md` | CloudEvents-compatible Attention Event、Evidence、PrivacyReport、DeliveryReport。 |
| 6 | `docs/06-capability-discovery.md` | Provider 如何声明自身能力，以及 Consumer 如何先发现再创建 Contract。 |
| 7 | `docs/07-lifecycle-api.md` | `eap.discover`、`eap.contract.create`、`eap.wait`、`eap.status`、`eap.attention.ack`、`eap.contract.revoke`。 |
| 8 | `docs/09-privacy-security.md` | 授权、consent、redaction、retention、audit、secret handling、agent action safety。 |
| 9 | `docs/16-standards-compatibility.md` | EAP 与 CloudEvents、AsyncAPI、OpenTelemetry、MQTT、NATS、OAuth、MCP、A2A 的关系。 |
| 10 | `docs/17-mcp-a2a-integration.md` | 如何把 EAP 映射成 MCP tools/resources 和 A2A tasks/artifacts。 |

完整目录见 `docs/00-index.md`，文件清单见 `MANIFEST.md`。

### 快速验证

```bash
cd /path/to/ExAP
python -m pip install jsonschema referencing PyYAML
python tests/conformance.py
```

当前包的一致性报告位于 `tests/conformance-report.md`。测试覆盖：

- schema meta-validation；
- canonical `$ref` 解析；
- valid examples；
- MCP tools 和 A2A Agent Card 示例；
- 7 个 domain profiles；
- negative fixtures；
- OpenAPI / AsyncAPI YAML；
- manifest 文件存在性；
- 规范文本中旧版本和模糊要求词检查；
- schema properties 文档覆盖；
- 全部 JSON 文件解析。

### Provider 实现路径

Provider 是观察环境、评估规则并交付事件的一方。一个 Provider-Minimal 实现需要覆盖：

1. 发布 capability document，列出支持的 EAP versions、subject types、signals、event types、operators、aggregates、delivery modes、privacy capabilities、limits 和 bindings。
2. 接收 `eap.contract.create`，用 `schemas/eap-attention-contract.schema.json` 校验 Contract。
3. 校验 EAP 版本、scope 授权、Subject 解析、Signal/Event 支持、Rule DSL capability、delivery mode、privacy policy 和 rule ID 唯一性。
4. 在后台采集 Observation 或 Event，按 Rule DSL 执行三值逻辑、window aggregate、debounce、cooldown、hysteresis 和 dedupe。
5. 生成 `eap.attention.triggered`、`eap.attention.recovered`、`eap.attention.summary` 或 state change 事件。
6. 在交付前执行 forbidden fields 检查、redaction、payload limits、retention 和 audit。
7. 支持 `eap.wait`、`eap.attention.ack` 和 `eap.contract.revoke`。

Provider 检查清单见 `templates/provider-checklist.md`。

### Consumer 与 agent 集成路径

Consumer 是创建 Contract 并接收 Attention Event 的一方。一个 Consumer-Minimal 或 Consumer-Agent 集成需要覆盖：

1. 调用 `eap.discover`，读取 Provider capability。
2. 选择 Provider 支持的 EAP 版本，创建满足 capability、authorization 和 privacy 限制的 Contract。
3. 使用 `blocking_wait`、`stream`、`push` 或 `pull_with_state_compression` 接收结果。
4. 对 Attention Event 执行 schema 校验，把 payload 视为不可信输入，只按 evidence 和 privacy report 处理可用信息。
5. 对 `requires_ack=true` 的事件执行 `eap.attention.ack`。
6. 关注结束后执行 `eap.contract.revoke`。
7. 遵守 Contract 的 `memory` policy；`memory.allowed=false` 时不把 payload、evidence 或 summary 写入长期记忆。

Consumer 检查清单见 `templates/consumer-checklist.md`。

### Agent 绑定

ExAP 为主流 agent 协议提供明确绑定点：

| Binding | 映射方式 |
|---|---|
| MCP | EAP Provider 作为 MCP server，暴露 `eap_discover`、`eap_contract_create`、`eap_wait`、`eap_status`、`eap_attention_ack`、`eap_contract_revoke` tools；capability、active contracts、recent attention、profiles 可作为 resources。 |
| A2A | EAP Provider 作为远程 agent，在 Agent Card 中声明 create contract 与 wait skill；Contract 创建和 wait 映射为 Task，Attention Event 作为 `application/eap+json` Artifact。 |

这个绑定保留 MCP 的 tool/resource 语义和 A2A 的 task lifecycle，同时让 EAP 专注于 environment-to-consumer awareness semantics。

### 场景覆盖

本包不把 EAP 限定为 coding agent。以下对象都可作为 Subject 或 Environment 的一部分：

- 邮件、会话、联系人和 inbox；
- 本地进程、进程组、日志和 job；
- GPU、磁盘、硬件与系统资源；
- 文件、目录和 artifact；
- 日历、会议、focus window；
- IoT device、sensor、gateway；
- CI/CD pipeline、build、deployment、release；
- cloud resource、queue、database、ticket、pull request；
- agent task、remote agent、workspace 和 generated artifact。

### 版本与兼容性

当前版本：`0.2.0-draft`。

版本规则见 `VERSION.md`：Provider 在 capability document 的 `eap_versions` 中列出支持版本；Consumer 在创建 Contract 前选择其中一个版本；Provider 拒绝未知 MAJOR 版本；同一发布包内 schema `$id` 保持唯一。

---

## English Version

### What ExAP is

ExAP is the specification package for EAP, the Environment Awareness Protocol. EAP defines a general contract layer for turning “tell me when this environment condition deserves attention” into structured, validated, auditable protocol objects.

It answers five questions:

1. Which Environment and Subjects a Consumer cares about.
2. Which Signals and Events a Provider can observe.
3. How the Rule DSL decides that something is worth attention.
4. How an Attention Event carries reason, evidence, severity, delivery action, and acknowledgement requirements.
5. How PrivacyPolicy constrains authorization, field-level redaction, data minimization, retention, audit, and agent memory.

ExAP currently ships the protocol specification, JSON Schemas, examples, domain profiles, binding references, and conformance tests. It is not yet a packaged runtime daemon; `docs/14-reference-implementation.md` defines the reference implementation boundaries for `eapd`, `eapctl`, `eap-mcp-server`, and `eap-a2a-agent`.

### Why EAP exists

Many agents and automation systems wait for external change by fixed-interval polling: a process exits, a GPU becomes idle, an email arrives, CI fails, a file appears, a calendar event starts, an IoT alarm fires, or a remote task finishes. Polling adds latency, noise, token and bandwidth cost, unclear privacy boundaries, and weak auditability.

EAP turns that waiting pattern into an explicit contract:

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

### What EAP does not replace

EAP sits above existing systems and does not replace them:

| Category | EAP boundary |
|---|---|
| CloudEvents | EAP Attention Event uses a CloudEvents-compatible envelope; CloudEvents remains the general event envelope standard. |
| AsyncAPI / OpenAPI | EAP can be described through them, but does not replace API description standards. |
| OpenTelemetry | EAP can consume metrics, logs, and traces as Observation, Event, or Evidence; telemetry collection stays outside EAP Core. |
| MQTT / NATS / Kafka / Webhook | EAP defines delivery semantics; the underlying transport remains responsible for transport behavior. |
| OAuth / mTLS / API key / IAM | EAP binds scope, consent, redaction, retention, and audit; existing security systems perform authentication and authorization. |
| MCP | MCP handles agent-to-tool/resource interaction; EAP exposes Lifecycle API through MCP tools. |
| A2A | A2A handles agent-to-agent tasks; EAP carries `application/eap+json` Attention Events as A2A artifacts. |

### What this package contains

| Surface | Content |
|---|---|
| Protocol version | `0.2.0-draft`. |
| Normative docs | `docs/00-index.md` through `docs/17-mcp-a2a-integration.md`, covering core model, Contract, Rule DSL, Event, Capability, Lifecycle, Transport, Privacy, Profiles, Conformance, MCP, and A2A. |
| JSON Schemas | 8 Draft 2020-12 schemas with canonical `$id` values under `https://eap.dev/schemas/`. |
| Examples | Contracts, Attention Events, Capability Documents, Lifecycle requests, MCP tools, A2A Agent Card, and local CLI examples. |
| Domain Profiles | Process monitoring, deep learning training, email priority, calendar focus, file watch, IoT safety, and CI/CD monitoring. |
| References | Draft OpenAPI for the HTTP binding and draft AsyncAPI for provider event streams. |
| Conformance | `tests/conformance.py` checks schemas, references, examples, profiles, negative fixtures, YAML references, manifest entries, and documentation coverage. |

### Core objects

| Object | Role |
|---|---|
| Environment | Boundary where awareness happens: a machine, workspace, project, home space, enterprise tenant, or cloud environment. |
| Subject | Observed object: mailbox, process, gpu, file, calendar, pipeline, iot_device, agent_task. |
| Signal | Observable state, metric, or property on a Subject, such as `process.cpu.percent`, `gpu.util.percent`, or `mail.message.received`. |
| Observation | Raw observation of a Signal at a point in time. |
| Event | Discrete event from a system API, SaaS webhook, log, queue, or sensor. |
| Capability Document | Machine-readable Provider declaration for EAP versions, Subjects, Signals, Events, Rules, Delivery, Privacy, limits, and bindings. |
| Attention Contract | Consumer-submitted contract containing intent, scope, rules, delivery, privacy, lifecycle, memory, and integrations. |
| Rule DSL | Structured JSON condition language with boolean, signal, event, state, correlation, window aggregate, debounce, cooldown, and hysteresis support. |
| Attention Event | Structured event delivered after a Rule match, carrying reason, severity, rule reference, evidence, payload, privacy report, and delivery report. |
| PrivacyPolicy / PrivacyReport | Declaration and report for data minimization, field-level redaction, forbidden fields, retention, audit, and consent. |

### Minimal reading path

| Order | File | What it gives you |
|---:|---|---|
| 1 | `docs/01-overview-and-scope.md` | Goals, non-goals, roles, and workflow. |
| 2 | `docs/02-core-model.md` | Environment, Subject, Signal, Observation, Event, Contract, Attention Event. |
| 3 | `docs/03-attention-contract.md` | How a Consumer expresses intent, scope, rules, delivery, privacy, and memory policy. |
| 4 | `docs/04-rule-dsl.md` | Conditions, operators, aggregates, debounce, cooldown, hysteresis, and missing-value semantics. |
| 5 | `docs/05-attention-event.md` | CloudEvents-compatible Attention Event, Evidence, PrivacyReport, and DeliveryReport. |
| 6 | `docs/06-capability-discovery.md` | How a Provider declares capability and how a Consumer discovers before creating a Contract. |
| 7 | `docs/07-lifecycle-api.md` | `eap.discover`, `eap.contract.create`, `eap.wait`, `eap.status`, `eap.attention.ack`, `eap.contract.revoke`. |
| 8 | `docs/09-privacy-security.md` | Authorization, consent, redaction, retention, audit, secret handling, and agent action safety. |
| 9 | `docs/16-standards-compatibility.md` | Relationship with CloudEvents, AsyncAPI, OpenTelemetry, MQTT, NATS, OAuth, MCP, and A2A. |
| 10 | `docs/17-mcp-a2a-integration.md` | How EAP maps to MCP tools/resources and A2A tasks/artifacts. |

See `docs/00-index.md` for the full manual and `MANIFEST.md` for the complete file map.

### Quick validation

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

### Provider implementation path

A Provider observes the environment, evaluates rules, and delivers events. A Provider-Minimal implementation covers:

1. Publish a capability document listing supported EAP versions, subject types, signals, event types, operators, aggregates, delivery modes, privacy capabilities, limits, and bindings.
2. Accept `eap.contract.create` and validate the Contract with `schemas/eap-attention-contract.schema.json`.
3. Validate EAP version, scope authorization, Subject resolution, Signal/Event support, Rule DSL capability, delivery mode, privacy policy, and rule ID uniqueness.
4. Collect Observations or Events in the background, then evaluate Rule DSL with three-valued logic, window aggregate, debounce, cooldown, hysteresis, and dedupe.
5. Generate `eap.attention.triggered`, `eap.attention.recovered`, `eap.attention.summary`, or state change events.
6. Apply forbidden-field checks, redaction, payload limits, retention, and audit before delivery.
7. Support `eap.wait`, `eap.attention.ack`, and `eap.contract.revoke`.

See `templates/provider-checklist.md` for the Provider checklist.

### Consumer and agent integration path

A Consumer creates Contracts and receives Attention Events. A Consumer-Minimal or Consumer-Agent integration covers:

1. Call `eap.discover` and read Provider capability.
2. Select a Provider-supported EAP version and create a Contract that fits capability, authorization, and privacy limits.
3. Receive results through `blocking_wait`, `stream`, `push`, or `pull_with_state_compression`.
4. Validate Attention Event schema, treat payload as untrusted input, and rely on evidence plus privacy report for usable context.
5. Execute `eap.attention.ack` for events with `requires_ack=true`.
6. Execute `eap.contract.revoke` when the attention need is over.
7. Respect the Contract `memory` policy; when `memory.allowed=false`, do not store payload, evidence, or summary in long-term memory.

See `templates/consumer-checklist.md` for the Consumer checklist.

### Agent bindings

ExAP defines explicit binding points for mainstream agent protocols:

| Binding | Mapping |
|---|---|
| MCP | EAP Provider acts as an MCP server and exposes `eap_discover`, `eap_contract_create`, `eap_wait`, `eap_status`, `eap_attention_ack`, and `eap_contract_revoke` tools; capability, active contracts, recent attention, and profiles can be resources. |
| A2A | EAP Provider acts as a remote agent and declares create-contract plus wait skills in its Agent Card; Contract creation and wait map to Tasks, and Attention Events are returned as `application/eap+json` Artifacts. |

This keeps MCP tool/resource semantics and A2A task lifecycle intact while EAP focuses on environment-to-consumer awareness semantics.

### Scenario coverage

EAP is not limited to coding agents. These objects can be Subjects or part of an Environment:

- email, threads, contacts, and inboxes;
- local processes, process groups, logs, and jobs;
- GPUs, disks, hardware, and system resources;
- files, directories, and artifacts;
- calendars, meetings, and focus windows;
- IoT devices, sensors, and gateways;
- CI/CD pipelines, builds, deployments, and releases;
- cloud resources, queues, databases, tickets, and pull requests;
- agent tasks, remote agents, workspaces, and generated artifacts.

### Version and compatibility

Current version: `0.2.0-draft`.

Version rules live in `VERSION.md`: Providers list supported versions in capability document `eap_versions`; Consumers select one before Contract creation; Providers reject unknown MAJOR versions; schema `$id` values stay unique within a release package.
