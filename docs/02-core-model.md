# 02. ExAP 核心对象模型

## 1. 统一数据格式

ExAP Core 对象使用 JSON。Schema 使用 JSON Schema Draft 2020-12。时间使用 RFC 3339 date-time 字符串。持续时间使用 ISO 8601 duration，例如 `PT5M`、`P1D`、`PT30S`。

## 2. ExAP URI

ExAP URI 标识 Environment、Subject、Provider 或其他 ExAP 对象。

格式：

```text
exap://<authority>/<type>/<id>
```

字段定义：

| 字段 | 定义 |
|---|---|
| `authority` | 命名空间。例：`local`、`personal`、`org-acme`。 |
| `type` | 对象类型。例：`process`、`gpu`、`mailbox`、`machine`。 |
| `id` | 命名空间内 ID。不得包含空白字符。 |

示例：

```text
exap://local/process/18423
exap://personal/mailbox/primary
exap://org-acme/pipeline/release-2026-05-16
```

## 3. Environment

Environment 是感知发生的边界。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `ref` | ExAP URI | 是 | Environment 标识。 |
| `kind` | string | 是 | 允许值：`personal`、`project`、`machine`、`home`、`enterprise`、`cloud`、`lab`、`service`、`custom`。 |
| `display_name` | string | 否 | 人类可读名称。 |
| `owner_ref` | ExAP URI | 否 | 所有者或控制者。 |
| `timezone` | string | 否 | IANA 时区名称。 |
| `labels` | object | 否 | 字符串、数字、布尔或 null 值组成的标签。 |
| `metadata` | object | 否 | 扩展元数据。 |

## 4. Subject

Subject 是被观察对象。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `ref` | ExAP URI | 是 | Subject 标识。 |
| `type` | string | 是 | Subject 类型。 |
| `environment_ref` | ExAP URI | 否 | 所属 Environment。 |
| `display_name` | string | 否 | 人类可读名称。 |
| `parent_ref` | ExAP URI | 否 | 父 Subject。 |
| `attributes` | object | 否 | Subject 属性。 |
| `sensitivity` | string | 否 | 允许值：`public`、`internal`、`confidential`、`secret`、`restricted`。 |
| `tags` | array[string] | 否 | 标签。 |
| `metadata` | object | 否 | 扩展元数据。 |

内置 subject type 名称不限定领域。Provider capability MUST 声明实际支持的类型。

## 5. Signal

Signal 是 Subject 上可观察的状态、指标或属性。Signal 名称使用点分层格式：

```text
<domain>.<entity>.<metric_or_property>
```

示例：

| Signal | 定义 |
|---|---|
| `process.status` | 进程状态。 |
| `process.cpu.percent` | 进程 CPU 使用率。 |
| `gpu.util.percent` | GPU 利用率。 |
| `mail.content.semantic_intent` | 邮件内容语义意图。 |
| `file.exists` | 文件是否存在。 |
| `device.temperature_c` | 设备温度。 |

Provider capability MUST 声明每个 Signal 的 value type、unit、支持的 operator 和适用 subject type。

## 6. Observation

Observation 是某一时刻对 Signal 的一次原始观测。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `observation_id` | string | 是 | Observation ID。 |
| `subject_ref` | ExAP URI | 是 | 被观察 Subject。 |
| `signal` | string | 是 | Signal 名称。 |
| `value` | any | 是 | 观测值。 |
| `observed_at` | date-time | 是 | 观测时间。 |
| `source` | string | 是 | 数据源。 |
| `quality` | object | 否 | 质量信息，例如 sampling interval、confidence。 |
| `privacy` | Privacy Report | 否 | 隐私报告。 |
| `trace` | TraceContext | 否 | 追踪信息。 |

## 7. Event

Event 是离散发生的事情。ExAP Event 可映射为 CloudEvents，也可作为 Provider 内部规则输入。

字段：

| 字段 | 定义 |
|---|---|
| `event_type` | 点分层事件名，例如 `process.exited`。 |
| `subject_ref` | 事件关联 Subject。 |
| `time` | 事件发生时间。 |
| `data` | 事件字段。 |

## 8. Attention Contract

Attention Contract 是 ExAP 的核心输入对象。它定义 Consumer、Provider、Scope、Rules、Delivery、Privacy、Lifecycle 和 Integration Hints。完整字段见 `03-attention-contract.md`。

## 9. Attention Event

Attention Event 是 ExAP 的核心输出对象。它使用 CloudEvents-compatible envelope，并在 `data` 中包含 ExAP 特有的 `attention_id`、`contract_id`、`status`、`severity`、`rule`、`evidence`、`privacy`、`delivery`。完整字段见 `05-attention-event.md`。

## 10. Severity

Severity 固定允许值：

| 值 | 定义 | 默认交付含义 |
|---|---|---|
| `info` | 信息性变化。 | 记录或摘要。 |
| `notice` | 需要普通注意。 | 可交付，不必打断。 |
| `warning` | 可能影响目标达成。 | 交付并可打断 wait。 |
| `critical` | 已发生失败、高风险或需要立即处理。 | 交付并打断 wait。 |
| `emergency` | 需要立即人工或系统级处置。 | 交付并打断 wait；Provider 可触发升级流程。 |
