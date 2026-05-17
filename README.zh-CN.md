<div align="center">

# ExAP

**External Awareness Protocol（外部感知协议）：用一个可验证的外部感知契约，声明谁关心什么、何时提醒、携带哪些证据、如何交付、如何保护隐私。**

面向需要外部世界感知能力的 agent、应用、服务、守护进程、broker 和运行时，避免用固定间隔轮询等待变化。

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

<p align="center">
  <a href="README.md">English</a> · <strong>简体中文</strong>
</p>

> ExAP 是 External Awareness Protocol 的规范包。
> 它面向需要外部世界感知能力的 agent、应用、服务、守护进程、broker 和运行时，用明确契约替代固定间隔轮询。
> Consumer 创建 Attention Contract；Provider 只观察契约声明的 scope，评估声明的规则，并返回带有 evidence、delivery metadata 和 privacy report 的 Attention Event。

---

## ExAP 是什么

ExAP（External Awareness Protocol）是一种通用的外部感知契约协议。它把“如果某个外部条件变得值得关注，请通知我”表达成结构化、可校验、可审计的协议对象。

ExAP 关注的是 agent、应用、服务或自动化系统与外部世界之间的注意力边界：哪些对象可以被观察，哪些信号可以被使用，什么条件算作值得提醒，事件如何交付，证据能携带到什么程度，隐私和授权如何被强制执行。

它回答五个问题：

1. Consumer 关心哪个 Environment 与哪些 Subject。
2. Provider 能观察哪些 Signal 与 Event。
3. Rule DSL 如何判断“值得注意”。
4. Attention Event 如何携带原因、证据、严重级别、交付动作和确认要求。
5. PrivacyPolicy 如何约束授权、字段级脱敏、数据最小化、保留期、审计和 agent memory。

ExAP 当前交付协议规范、JSON Schema、示例、领域 Profile、绑定参考和一致性测试。当前包聚焦协议表面；`docs/14-reference-implementation.md` 固定未来参考实现的组件边界，包括 `exapd`、`exapctl`、`exap-mcp-server` 和 `exap-a2a-agent`。

## 为什么需要 ExAP

许多 agent 和自动化系统会用固定间隔轮询来等待外部世界变化：进程结束、GPU 空闲、邮件到达、CI 失败、文件出现、日历开始、IoT 告警、远程任务完成。轮询会带来延迟、噪声、token/带宽浪费、隐私边界模糊和审计困难。

ExAP 把这种等待改成显式契约：

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

这使外部感知从“持续询问现在怎么样了”变成“只在明确条件满足时交付经过约束的事件”。

## 标准与绑定位置

ExAP 作为关注契约层，与现有事件、遥测、传输、安全和 agent 协议配合使用：

| 类别 | ExAP 的接入方式 |
|---|---|
| CloudEvents | ExAP Attention Event 使用 CloudEvents-compatible envelope，并补充 attention reason、evidence、privacy report 和 delivery report。 |
| AsyncAPI / OpenAPI | AsyncAPI 和 OpenAPI 描述 ExAP message channel、HTTP binding、lifecycle request 和 event stream。 |
| OpenTelemetry | metrics、logs、traces 可进入 ExAP Observation、Event 或 Evidence。 |
| MQTT / NATS / Kafka / Webhook | 这些传输承载 ExAP delivery mode；ExAP 提供 contract、rule、delivery 和 acknowledgement 语义。 |
| OAuth / mTLS / API key / IAM | 现有安全系统提供 identity 与 authorization；ExAP 将 scope、consent、redaction、retention 和 audit 绑定到每个 Contract。 |
| MCP | MCP 将 ExAP Lifecycle API 暴露为 tools，并将 capability、active contracts、recent attention 和 profiles 发布为 resources。 |
| A2A | A2A 将 create-contract 与 wait 流程映射为 tasks，并以 `application/exap+json` artifact 返回 Attention Event。 |

## 当前包内容

| Surface | 内容 |
|---|---|
| Protocol version | `0.2.0-draft`。 |
| Normative docs | `docs/00-index.md` 到 `docs/17-mcp-a2a-integration.md`，覆盖核心模型、Contract、Rule DSL、Event、Capability、Lifecycle、Transport、Privacy、Profiles、Conformance、MCP、A2A。 |
| JSON Schemas | 8 个 Draft 2020-12 schema，canonical `$id` 位于 `https://exap.dev/schemas/`。 |
| Examples | Contract、Attention Event、Capability Document、Lifecycle request、MCP tools、A2A Agent Card、local CLI 样例。 |
| Domain Profiles | process monitoring、deep learning training、email priority、calendar focus、file watch、IoT safety、CI/CD monitoring。 |
| References | HTTP binding 的 OpenAPI 草案与 provider event stream 的 AsyncAPI 草案。 |
| Conformance | `tests/conformance.py` 执行 schema、引用、示例、profile、负面用例、YAML、清单和文档覆盖检查。 |

## 核心对象

| 对象 | 作用 |
|---|---|
| Environment | 外部感知发生的边界，例如机器、工作区、项目、家庭空间、企业租户或云环境。 |
| Subject | 被观察对象，例如 mailbox、process、gpu、file、calendar、pipeline、iot_device、agent_task。 |
| Signal | Subject 上可观察的状态、指标或属性，例如 `process.cpu.percent`、`gpu.util.percent`、`mail.message.received`。 |
| Observation | 对某个 Signal 在某一时刻的原始观测。 |
| Event | 离散事件，可来自系统 API、SaaS webhook、日志、队列或传感器。 |
| Capability Document | Provider 对 ExAP 版本、Subject、Signal、Event、Rule、Delivery、Privacy、limits、bindings 的机器可读声明。 |
| Attention Contract | Consumer 提交给 Provider 的关注契约，包含 intent、scope、rules、delivery、privacy、lifecycle、memory 和 integrations。 |
| Rule DSL | 用结构化 JSON 表达条件，支持 boolean、signal、event、state、correlation、window aggregate、debounce、cooldown、hysteresis。 |
| Attention Event | Rule 触发后交付给 Consumer 的结构化事件，包含 reason、severity、rule reference、evidence、payload、privacy report、delivery report。 |
| PrivacyPolicy / PrivacyReport | 声明和报告数据最小化、字段级脱敏、禁止字段、保留期、审计和 consent。 |

## 最小阅读路径

| 顺序 | 文件 | 读完后能理解什么 |
|---:|---|---|
| 1 | `docs/01-overview-and-scope.md` | ExAP 的目标、非目标、角色和工作流。 |
| 2 | `docs/02-core-model.md` | Environment、Subject、Signal、Observation、Event、Contract、Attention Event。 |
| 3 | `docs/03-attention-contract.md` | Consumer 如何表达 intent、scope、rules、delivery、privacy 和 memory policy。 |
| 4 | `docs/04-rule-dsl.md` | Rule 条件、operator、aggregate、debounce、cooldown、hysteresis 和缺失值语义。 |
| 5 | `docs/05-attention-event.md` | CloudEvents-compatible Attention Event、Evidence、PrivacyReport、DeliveryReport。 |
| 6 | `docs/06-capability-discovery.md` | Provider 如何声明自身能力，以及 Consumer 如何先发现再创建 Contract。 |
| 7 | `docs/07-lifecycle-api.md` | `exap.discover`、`exap.contract.create`、`exap.wait`、`exap.status`、`exap.attention.ack`、`exap.contract.revoke`。 |
| 8 | `docs/09-privacy-security.md` | 授权、consent、redaction、retention、audit、secret handling、agent action safety。 |
| 9 | `docs/16-standards-compatibility.md` | ExAP 与 CloudEvents、AsyncAPI、OpenTelemetry、MQTT、NATS、OAuth、MCP、A2A 的关系。 |
| 10 | `docs/17-mcp-a2a-integration.md` | 如何把 ExAP 映射成 MCP tools/resources 和 A2A tasks/artifacts。 |

完整目录见 `docs/00-index.md`，文件清单见 `MANIFEST.md`。

## 快速验证

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

## Provider 实现路径

Provider 是观察外部环境、评估规则并交付事件的一方。一个 Provider-Minimal 实现需要覆盖：

1. 发布 capability document，列出支持的 ExAP versions、subject types、signals、event types、operators、aggregates、delivery modes、privacy capabilities、limits 和 bindings。
2. 接收 `exap.contract.create`，并用 `schemas/` 下的 attention contract schema 校验 Contract。
3. 校验 ExAP 版本、scope 授权、Subject 解析、Signal/Event 支持、Rule DSL capability、delivery mode、privacy policy 和 rule ID 唯一性。
4. 在后台采集 Observation 或 Event，按 Rule DSL 执行三值逻辑、window aggregate、debounce、cooldown、hysteresis 和 dedupe。
5. 生成 `exap.attention.triggered`、`exap.attention.recovered`、`exap.attention.summary` 或 state change 事件。
6. 在交付前执行 forbidden fields 检查、redaction、payload limits、retention 和 audit。
7. 支持 `exap.wait`、`exap.attention.ack` 和 `exap.contract.revoke`。

Provider 检查清单见 `templates/provider-checklist.md`。

## Consumer 与 agent 集成路径

Consumer 是创建 Contract 并接收 Attention Event 的一方。一个 Consumer-Minimal 或 Consumer-Agent 集成需要覆盖：

1. 调用 `exap.discover`，读取 Provider capability。
2. 选择 Provider 支持的 ExAP 版本，创建满足 capability、authorization 和 privacy 限制的 Contract。
3. 使用 `blocking_wait`、`stream`、`push` 或 `pull_with_state_compression` 接收结果。
4. 对 Attention Event 执行 schema 校验，把 payload 作为未信任输入处理，仅按 evidence 和 privacy report 处理可用信息。
5. 对 `requires_ack=true` 的事件执行 `exap.attention.ack`。
6. 关注结束后执行 `exap.contract.revoke`。
7. 遵守 Contract 的 `memory` policy；`memory.allowed=false` 时，将 payload、evidence 或 summary 限定在短期处理流程内，长期记忆只保存策略允许的信息。

Consumer 检查清单见 `templates/consumer-checklist.md`。

## Agent 绑定

ExAP 为主流 agent 协议提供明确绑定点：

| Binding | 映射方式 |
|---|---|
| MCP | ExAP Provider 作为 MCP server，暴露 `exap_discover`、`exap_contract_create`、`exap_wait`、`exap_status`、`exap_attention_ack`、`exap_contract_revoke` tools；capability、active contracts、recent attention、profiles 可作为 resources。 |
| A2A | ExAP Provider 作为远程 agent，在 Agent Card 中声明 create contract 与 wait skill；Contract 创建和 wait 映射为 Task，Attention Event 作为 `application/exap+json` Artifact。 |

这个绑定保留 MCP 的 tool/resource 语义和 A2A 的 task lifecycle，同时让 ExAP 专注于 external-to-consumer awareness semantics。

## 场景覆盖

ExAP 覆盖 coding agent、自动化系统、本地机器、SaaS 表面和物理环境。以下对象都可作为 Subject 或 Environment 的一部分：

- 邮件、会话、联系人和 inbox；
- 本地进程、进程组、日志和 job；
- GPU、磁盘、硬件与系统资源；
- 文件、目录和 artifact；
- 日历、会议、focus window；
- IoT device、sensor、gateway；
- CI/CD pipeline、build、deployment、release；
- cloud resource、queue、database、ticket、pull request；
- agent task、remote agent、workspace 和 generated artifact。

## 版本与兼容性

当前版本：`0.2.0-draft`。

版本规则见 `VERSION.md`：Provider 在 capability document 的 `exap_versions` 中列出支持版本；Consumer 在创建 Contract 前选择其中一个版本；Provider 拒绝未知 MAJOR 版本；同一发布包内 schema `$id` 保持唯一。
