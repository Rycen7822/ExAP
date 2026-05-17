# 05. Attention Event

## 1. 定义

Attention Event 是 Provider 评估 Rule 后交付给 Consumer 的结构化事件。Attention Event 使用 CloudEvents-compatible envelope，`data` 字段承载 EAP 专用内容。

Attention Event JSON MUST 使用 `schemas/eap-attention-event.schema.json` 校验通过。

## 2. CloudEvents-compatible envelope

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `specversion` | string | 是 | 必须为 `1.0`。 |
| `id` | string | 是 | Event ID。MUST 唯一。 |
| `source` | string | 是 | Provider source。可使用 EAP URI。 |
| `type` | string | 是 | `eap.attention.triggered`、`eap.attention.recovered`、`eap.attention.summary`、`eap.attention.acknowledged`、`eap.contract.state_changed`。 |
| `subject` | string | 否 | 主 Subject 引用。 |
| `time` | date-time | 是 | 事件生成时间。 |
| `datacontenttype` | string | 是 | 必须为 `application/json`。 |
| `data` | AttentionData | 是 | EAP 事件数据。 |

## 3. `data` 字段

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `eap_version` | string | 是 | EAP 版本。 |
| `attention_id` | string | 是 | Attention ID。格式 `attn_<id>`。 |
| `contract_id` | string | 是 | 触发 Contract ID。 |
| `status` | string | 是 | `triggered`、`recovered`、`summary`、`acknowledged`、`suppressed`、`state_changed`。 |
| `severity` | string | 是 | Severity。 |
| `title` | string | 是 | 160 字符以内标题。 |
| `reason` | string | 是 | 触发原因。 |
| `intent` | string | 否 | Contract intent。 |
| `subject` | Subject | 是 | 主 Subject 快照。 |
| `rule` | RuleReference | 是 | 触发 Rule 信息。 |
| `evidence` | array[EvidenceItem] | 是 | 证据项。`status=triggered` 时长度 MUST 大于 0。 |
| `payload` | object | 否 | 领域 payload。必须受 PrivacyPolicy 约束。 |
| `privacy` | PrivacyReport | 是 | 实际包含、脱敏和保留报告。 |
| `delivery` | DeliveryReport | 是 | 交付动作和 ack 要求。 |
| `trace` | TraceContext | 否 | 追踪信息。 |
| `links` | array[object] | 否 | 相关资源链接。 |

## 4. RuleReference

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `rule_id` | string | 是 | Rule ID。 |
| `name` | string | 是 | Rule name。 |
| `severity` | string | 是 | Rule severity。 |
| `condition_summary` | string | 是 | 触发条件摘要。 |
| `matched_at` | date-time | 是 | 匹配时间。 |

## 5. EvidenceItem

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `evidence_id` | string | 是 | Evidence ID。 |
| `kind` | string | 是 | Evidence 类型。 |
| `subject_ref` | EAP URI | 是 | 证据关联 Subject。 |
| `signal` | string | 否 | Signal 名称。 |
| `event_type` | string | 否 | Event type。 |
| `observed_at` | date-time | 是 | 观测或事件时间。 |
| `window` | duration | 否 | 聚合窗口。 |
| `value` | any | 否 | 观测值或匹配值。 |
| `unit` | string | 否 | 单位。 |
| `stats` | object | 否 | 窗口统计。 |
| `excerpt` | string | 否 | 日志、消息或文本摘录。 |
| `score` | number | 否 | 语义或置信度分数。 |
| `path` | string | 否 | 字段或文件路径。 |
| `redacted` | boolean | 否 | 是否已脱敏。 |
| `metadata` | object | 否 | 扩展元数据。 |

Evidence `kind` 允许值：

| kind | 定义 |
|---|---|
| `signal_value` | 单点 Signal 值。 |
| `signal_window` | 窗口聚合统计。 |
| `event_match` | 匹配的 Event 摘要。 |
| `log_excerpt` | 日志摘录。 |
| `semantic_score` | 语义匹配结果。 |
| `subject_snapshot` | Subject 快照。 |
| `trace_link` | Trace 或 span 链接。 |
| `redaction_report` | 脱敏处理证据。 |

## 6. PrivacyReport

PrivacyReport 说明事件实际包含了什么字段，哪些字段被脱敏，数据保留多久。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `purpose` | string | 是 | 数据处理目的。 |
| `data_minimization_applied` | boolean | 是 | 是否执行最小化。 |
| `fields_included` | array[string] | 是 | 实际包含字段。 |
| `fields_redacted` | array[string] | 是 | 已脱敏或删除字段。 |
| `retention` | object | 是 | 各类数据保留期。 |
| `redaction_report` | array[object] | 否 | 脱敏详情。 |

Provider MUST 确保 `fields_included` 不包含 Contract `privacy.forbidden_fields`。

## 7. DeliveryReport

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `action` | DeliveryAction | 是 | 实际交付动作。 |
| `requires_ack` | boolean | 是 | 是否需要 ack。 |
| `ack_deadline` | duration | 否 | ack 截止时间。 |
| `transport` | string | 否 | 实际 transport。 |
| `attempt` | integer | 否 | 第几次交付尝试。 |

## 8. Ack 事件

Consumer 执行 `eap.attention.ack` 后，Provider MAY 产生 `eap.attention.acknowledged` 事件。Ack 事件的 `data.status` MUST 为 `acknowledged`，`data.rule` MUST 指向原 Rule，`data.payload` MUST 包含 ack action、actor 和 ack time。

## 9. Summary Event

Summary Event 的 `type` 为 `eap.attention.summary`，`data.status` 为 `summary`。Summary Event 用于交付被 `include_in_summary` 聚合的事件或周期状态。Summary Event 的 evidence MAY 为空。

## 10. TraceContext

TraceContext 字段：

| 字段 | 类型 | 定义 |
|---|---:|---|
| `trace_id` | string | 分布式追踪 ID。 |
| `span_id` | string | 当前 span ID。 |
| `parent_span_id` | string | 父 span ID。 |
| `correlation_id` | string | 跨系统关联 ID。 |

## 11. Suppression

Provider 抑制重复事件时 MAY 记录 `data.status=suppressed` 的内部事件。若交付给 Consumer，Provider MUST 在 `reason` 中说明抑制原因，在 `payload` 中包含 suppressed count。
