# 03. Attention Contract

## 1. 定义

Attention Contract 是 Consumer 提交给 Provider 的规范化关注契约。Provider 只按照 Contract 中明确声明的 scope、rules、delivery 和 privacy 观察环境并交付 Attention Event。

Contract JSON MUST 使用 `schemas/exap-attention-contract.schema.json` 校验通过。

## 2. 顶层字段

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `exap_version` | string | 是 | 无 | ExAP 版本。当前包使用 `0.2.0-draft`。 |
| `contract_id` | string | 否 | Provider 生成 | Contract ID。格式为 `act_<id>`。Consumer 提供时在 Provider 范围内 MUST 唯一。 |
| `created_at` | date-time | 否 | Provider 当前时间 | Contract 创建时间。 |
| `updated_at` | date-time | 否 | Provider 当前时间 | Contract 最近更新时间。 |
| `created_by` | string | 否 | `consumer.consumer_id` | 创建者标识。 |
| `consumer` | Consumer | 是 | 无 | 接收事件的实体。 |
| `provider` | Provider | 否 | 当前 Provider | 执行 Contract 的实体。 |
| `environment` | Environment | 否 | 无 | 内联 Environment 对象。 |
| `environment_ref` | ExAP URI | 否 | Provider 默认环境 | Environment 引用。`environment` 与 `environment_ref` 同时存在时，二者 MUST 指向同一环境。 |
| `intent` | string | 是 | 无 | 关注意图。MUST 是非空字符串。 |
| `scope` | Scope | 是 | 无 | 观察范围。 |
| `rules` | array[Rule] | 是 | 无 | 触发规则。长度 MUST 大于 0。 |
| `delivery` | Delivery | 是 | 无 | 交付模式、传输、返回策略和 ack 策略。 |
| `privacy` | PrivacyPolicy | 是 | 无 | 用途、数据最小化、脱敏、保留和审计策略。 |
| `lifecycle` | Lifecycle | 否 | Provider 填充 | Contract 生命周期。 |
| `state_policy` | StatePolicy | 否 | Provider 默认 | 观测和事件状态存储策略。 |
| `memory` | MemoryPolicy | 否 | `allowed=false` | Consumer 或 agent 是否允许持久化 ExAP 信息。 |
| `integrations` | IntegrationHints | 否 | `{}` | MCP、A2A、OpenTelemetry 等集成提示。 |
| `metadata` | object | 否 | `{}` | 扩展元数据。 |

## 3. `consumer`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `consumer_id` | string | 是 | Consumer 唯一标识。例：`agent:codex-local`。 |
| `type` | string | 是 | 允许值：`agent`、`application`、`service`、`user_interface`、`automation`、`human_proxy`、`custom`。 |
| `display_name` | string | 否 | 人类可读名称。 |
| `instance_id` | string | 否 | Consumer 实例 ID。 |
| `capabilities` | object | 否 | Consumer 接收能力。 |
| `auth_context` | object | 否 | 已认证上下文引用。MUST NOT 包含明文 secret。 |
| `metadata` | object | 否 | 扩展元数据。 |

## 4. `provider`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `provider_id` | string | 是 | Provider 唯一标识。 |
| `type` | string | 是 | 允许值：`local_daemon`、`connector`、`monitoring_service`、`broker`、`iot_gateway`、`cloud_service`、`agent_runtime`、`custom`。 |
| `display_name` | string | 否 | 名称。 |
| `version` | string | 否 | Provider 版本。 |
| `capability_ref` | string | 否 | Capability document 引用。 |
| `endpoint` | string | 否 | Provider endpoint。 |
| `authority` | string | 否 | Provider 命名空间。 |
| `metadata` | object | 否 | 扩展元数据。 |

## 5. `scope`

Scope 定义 Contract 可观察范围。Provider MUST 拒绝超出 capability 或授权范围的 Scope。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `subjects` | array[SubjectSelector] | 是 | 观察对象选择器。长度 MUST 大于 0。 |
| `signals` | array[string] | 否 | 允许观察的 Signal 白名单。省略时仅允许规则引用的 Signal。 |
| `events` | array[string] | 否 | 允许观察的 Event type 白名单。省略时仅允许规则引用的 Event。 |
| `time_window` | TimeWindow | 否 | 有效观察时间窗口。 |
| `labels` | object | 否 | 标签过滤。 |

### 5.1 SubjectSelector

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `type` | string | 是 | 无 | Subject 类型。 |
| `ref` | ExAP URI | 条件必填 | 无 | 精确 Subject 引用。 |
| `match` | object | 条件必填 | 无 | 动态属性匹配。`ref` 与 `match` MUST 至少存在一个。 |
| `include_children` | boolean | 否 | `false` | 是否包含子 Subject。 |
| `relationship` | string | 否 | 无 | 与其他 Subject 的关系。 |
| `resolution` | string | 否 | `exact` | 允许值：`exact`、`dynamic`、`snapshot`。 |

`resolution` 语义：

| 值 | 定义 |
|---|---|
| `exact` | Provider 在创建时解析为固定 Subject。 |
| `dynamic` | Provider 在运行期间持续匹配新增或变化的 Subject。 |
| `snapshot` | Provider 在创建时解析匹配集合，之后不纳入新增 Subject。 |

### 5.2 TimeWindow

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `starts_at` | date-time | 否 | Contract 激活时间 | 开始观察时间。 |
| `ends_at` | date-time | 否 | `lifecycle.expires_at` | 结束观察时间。超过该时间 Provider MUST 停止观察并将 Contract 置为 `expired`。 |
| `timezone` | string | 否 | Environment timezone | 用于日历语义的人类时区。绝对时间仍由 date-time 决定。 |

## 6. `rules`

`rules` 是 Rule 对象数组。Rule 完整定义见 `04-rule-dsl.md`。

规则：

- `rule_id` 在同一 Contract 内 MUST 唯一。
- 至少存在一个 `enabled` 不为 `false` 的 Rule。
- Rule 中引用的 Signal MUST 在 Provider capability 中存在。
- Rule 中引用的 Event type MUST 在 Provider capability 中存在。
- Rule 中使用的 operator、aggregate、condition type MUST 在 Provider capability 中存在。

## 7. `delivery`

Delivery 定义事件交付方式。

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `modes` | array[string] | 是 | 无 | 允许值：`blocking_wait`、`push`、`stream`、`pull_with_state_compression`。 |
| `transports` | array[Transport] | 是 | `[]` | 传输配置。 |
| `return_policy` | ReturnPolicy | 是 | 无 | severity 到 delivery action 的映射。 |
| `dedupe` | Dedupe | 否 | 无 | 去重策略。 |
| `retry` | Retry | 否 | 无 | 推送重试策略。 |
| `ack` | AckPolicy | 否 | `required=false` | 确认策略。 |
| `payload_limits` | PayloadLimits | 否 | Provider 默认 | Payload 大小限制。 |

### 7.1 Transport

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `transport` | string | 是 | 允许值：`http`、`http_webhook`、`sse`、`websocket`、`mqtt`、`nats`、`kafka`、`local_stdio`、`local_socket`、`mcp`、`a2a`。 |
| `mode` | string | 是 | 该 transport 绑定的 delivery mode。 |
| `content_mode` | string | 是 | `structured` 或 `binary`。 |
| `endpoint` | string | 否 | HTTP、SSE、WebSocket、MCP、A2A 或 local endpoint。 |
| `topic` | string | 否 | MQTT 或 Kafka topic。 |
| `subject` | string | 否 | NATS subject。 |
| `auth_ref` | string | 否 | 凭据引用。MUST NOT 存放明文 secret。 |
| `metadata` | object | 否 | 绑定元数据。 |

### 7.2 ReturnPolicy

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `default_action` | DeliveryAction | 是 | 未匹配 severity 时的动作。 |
| `by_severity` | object | 是 | `info`、`notice`、`warning`、`critical`、`emergency` 到 DeliveryAction 的映射。 |

DeliveryAction 允许值：

| 值 | 定义 |
|---|---|
| `record_only` | 只记录，不交付给 Consumer。 |
| `include_in_summary` | 不立即交付，只在 summary 中出现。 |
| `deliver` | 交付给 Consumer，不打断 blocking wait 以外的执行。 |
| `deliver_and_interrupt_wait` | 交付给 Consumer，并使阻塞中的 `exap.wait` 立即返回。 |

Rule 的 `delivery_action` 存在时覆盖 ReturnPolicy。

### 7.3 Dedupe

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `key_fields` | array[string] | 否 | 用于去重的字段路径。 |
| `window` | duration | 否 | 去重时间窗。 |

Provider 对同一 dedupe key 在 window 内 MUST 只交付一次，除非 severity 升级。

### 7.4 Retry

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `max_attempts` | integer | 否 | 最大重试次数。`0` 表示不重试。 |
| `backoff` | string | 否 | `none`、`fixed`、`exponential`。 |
| `initial_delay` | duration | 否 | 初始重试间隔。 |
| `max_delay` | duration | 否 | 最大重试间隔。 |

### 7.5 AckPolicy

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `required` | boolean | 是 | 是否需要 ack。 |
| `deadline` | duration | 是 | ack 截止时间。`PT0S` 表示无截止。 |
| `snooze_allowed` | boolean | 否 | 是否允许 snooze。 |

### 7.6 PayloadLimits

| 字段 | 类型 | 定义 |
|---|---:|---|
| `max_event_bytes` | integer | 单个 Attention Event 最大字节数。 |
| `max_evidence_items` | integer | Evidence 数量上限。 |
| `max_text_chars` | integer | 文本 excerpt 最大字符数。 |

Provider MUST 在超限前执行摘要、裁剪或脱敏，并在 Privacy Report 或 Evidence metadata 中记录。

## 8. `privacy`

PrivacyPolicy 完整字段：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `purpose` | string | 是 | 数据处理目的。 |
| `data_minimization` | boolean | 是 | 是否强制数据最小化。 |
| `allowed_fields` | array[string] | 否 | 允许出现在事件中的字段路径。 |
| `forbidden_fields` | array[string] | 是 | 禁止出现在事件中的字段路径。 |
| `redaction` | object | 是 | 脱敏配置。 |
| `retention` | object | 是 | Observation、event、audit log 保留期。 |
| `audit` | object | 是 | 审计配置。 |
| `consent_ref` | string | 否 | 用户或组织 consent 引用。 |
| `data_classes` | array[string] | 否 | 数据分类。 |

Provider MUST 在事件交付前执行 `forbidden_fields` 检查。任何 forbidden field 出现在 payload、evidence 或 metadata 中时，Provider MUST 删除或脱敏该字段。

## 9. `lifecycle`

| 字段 | 类型 | 定义 |
|---|---:|---|
| `status` | string | `draft`、`active`、`paused`、`revoked`、`expired`、`completed`、`failed`。 |
| `starts_at` | date-time | Contract 激活时间。 |
| `expires_at` | date-time | 到期时间。 |
| `max_runtime` | duration | 最长运行时间。 |
| `auto_revoke_on_completion` | boolean | `completed` 后是否自动 revoke。 |

状态转换：

```text
draft -> active
active -> paused -> active
active -> completed
active -> expired
active -> revoked
active -> failed
paused -> revoked
paused -> expired
```

终态：`revoked`、`expired`、`completed`、`failed`。终态 Contract MUST NOT 再进入 `active`。

## 10. `state_policy`

| 字段 | 类型 | 定义 |
|---|---:|---|
| `store_observations` | boolean | 是否存储 Observation。 |
| `store_events` | boolean | 是否存储 Attention Event。 |
| `checkpoint_interval` | duration | Provider 状态 checkpoint 周期。 |

## 11. `memory`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `allowed` | boolean | 是 | Consumer 或 agent 是否允许持久化来自 ExAP 的信息。 |
| `scope` | string | 是 | `none`、`session`、`project`、`user`、`organization`。 |
| `allowed_keys` | array[string] | 否 | 允许持久化的键。 |
| `forbidden_keys` | array[string] | 否 | 禁止持久化的键。 |

`memory.allowed=false` 时，Consumer MUST NOT 将 ExAP payload、evidence 或 summary 写入长期记忆。

## 12. `integrations`

| 字段 | 类型 | 定义 |
|---|---:|---|
| `mcp` | object | MCP 绑定提示，例如 tool 名称、resource URI。 |
| `a2a` | object | A2A 绑定提示，例如 artifact media type、context id。 |
| `opentelemetry` | object | OpenTelemetry 追踪或资源属性映射。 |
