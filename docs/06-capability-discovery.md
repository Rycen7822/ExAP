# 06. Capability Discovery

## 1. 定义

Capability Discovery 是 Consumer 对 Provider 的第一步调用。Provider 返回 Capability Document，说明自己支持的 EAP 版本、Subject、Signal、Event、Rule、Delivery、Privacy、limits、bindings、profiles 和 actions。

Capability JSON MUST 使用 `schemas/eap-capability.schema.json` 校验通过。

## 2. Discover 请求

`eap.discover` 请求参数：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `environment_ref` | EAP URI | 否 | 限定 Environment。 |
| `subject_types` | array[string] | 否 | 限定返回的 Subject 类型。 |
| `signals` | array[string] | 否 | 限定返回的 Signal。 |
| `profiles` | array[string] | 否 | 限定返回的 Profile。 |
| `include_examples` | boolean | 否 | 是否返回示例片段。 |

## 3. Capability Document 顶层字段

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `eap_versions` | array[string] | 是 | 支持的 EAP 版本。 |
| `capability_id` | string | 是 | Capability document ID。 |
| `provider` | Provider | 是 | Provider 身份。 |
| `environments` | array[Environment] | 否 | Provider 可观察的 Environment。 |
| `subject_types` | array[SubjectTypeCapability] | 是 | Subject 类型能力。 |
| `signals` | array[SignalCapability] | 是 | Signal 能力。 |
| `event_types` | array[EventTypeCapability] | 是 | Event 类型能力。 |
| `rule_capabilities` | RuleCapabilities | 是 | Rule DSL 能力。 |
| `delivery_capabilities` | DeliveryCapabilities | 是 | 交付能力。 |
| `privacy_capabilities` | PrivacyCapabilities | 是 | 隐私能力。 |
| `limits` | object | 是 | 限制。 |
| `bindings` | array[BindingCapability] | 否 | 传输绑定能力。 |
| `profiles` | array[object] | 否 | 支持的 Domain Profile。 |
| `actions` | array[object] | 否 | Provider 支持的动作。动作不属于 Core 自动执行流程。 |
| `metadata` | object | 否 | 扩展元数据。 |

## 4. SubjectTypeCapability

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | Subject 类型。 |
| `description` | string | 是 | 类型说明。 |
| `discoverable` | boolean | 是 | Consumer 是否可列举该类型 Subject。 |
| `relationships` | array[string] | 否 | 支持的关系。 |
| `attributes` | array[string] | 否 | 可返回属性。 |
| `sensitivity` | string | 否 | 默认敏感级别。 |

## 5. SignalCapability

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `name` | string | 是 | Signal 名称。 |
| `subject_types` | array[string] | 是 | 适用 Subject 类型。 |
| `value_type` | string | 是 | `number`、`integer`、`string`、`boolean`、`datetime`、`duration`、`object`、`array`、`null`。 |
| `unit` | string | 否 | 单位。 |
| `description` | string | 是 | Signal 说明。 |
| `operators` | array[string] | 是 | 支持的 operator。 |
| `sampling` | object | 否 | 采样能力。 |
| `privacy_class` | string | 否 | 隐私分类。 |

## 6. EventTypeCapability

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `event_type` | string | 是 | Event type。 |
| `subject_types` | array[string] | 是 | 适用 Subject 类型。 |
| `description` | string | 是 | 说明。 |
| `fields` | array[string] | 否 | Event data 字段。 |
| `privacy_class` | string | 否 | 隐私分类。 |

## 7. RuleCapabilities

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `condition_types` | array[string] | 是 | 支持的 Condition type。 |
| `operators` | array[string] | 是 | 支持的 operator。 |
| `aggregates` | array[string] | 是 | 支持的 aggregate。 |
| `hysteresis` | boolean | 是 | 是否支持 hysteresis。 |
| `cooldown` | boolean | 是 | 是否支持 cooldown。 |
| `correlation` | boolean | 是 | 是否支持 correlation。 |
| `semantic_match` | boolean | 是 | 是否支持 semantic_match。 |

Provider MUST 拒绝不在 capability 中的 operator、condition type 和 aggregate。

## 8. DeliveryCapabilities

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `modes` | array[string] | 是 | 支持的 delivery modes。 |
| `transports` | array[string] | 是 | 支持的 transports。 |
| `content_modes` | array[string] | 是 | `structured` 或 `binary`。 |
| `supports_ack` | boolean | 是 | 是否支持 ack。 |
| `supports_snooze` | boolean | 是 | 是否支持 snooze。 |
| `max_wait` | duration | 否 | 最大 wait 时长。 |

## 9. PrivacyCapabilities

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `field_level_access` | boolean | 是 | 是否支持字段级访问控制。 |
| `redaction_methods` | array[string] | 是 | 支持的脱敏方法。 |
| `retention_controls` | boolean | 是 | 是否支持保留期控制。 |
| `audit_log` | boolean | 是 | 是否支持审计日志。 |
| `consent_required` | boolean | 否 | 是否需要显式 consent。 |

## 10. BindingCapability

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `binding` | string | 是 | `http`、`webhook`、`sse`、`websocket`、`mqtt`、`nats`、`kafka`、`local_stdio`、`local_socket`、`mcp`、`a2a`。 |
| `endpoint` | string | 是 | 绑定 endpoint。 |
| `auth` | array[string] | 否 | 支持的认证方式。 |
| `metadata` | object | 否 | 绑定元数据。 |

## 11. Limits

`limits` MUST 至少包含 Provider 认为会影响 Contract 创建或 Delivery 的限制，例如：

| 字段 | 定义 |
|---|---|
| `max_contracts` | 最大 Contract 数。 |
| `max_rules_per_contract` | 单 Contract 最大 Rule 数。 |
| `max_wait` | 最大 wait 时长。 |
| `max_payload_bytes` | 最大事件 payload 字节数。 |
| `max_regex_length` | 最大 regex 长度。 |
| `min_sampling_interval` | 最小采样间隔。 |
