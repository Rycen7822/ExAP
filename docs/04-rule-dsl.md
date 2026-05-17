# 04. ExAP Rule DSL

## 1. 定义

Rule DSL 是 ExAP 中表达“何时值得注意”的结构化 JSON 语言。Rule DSL MUST NOT 使用任意代码字符串作为可执行表达式。Provider MUST 在 Contract 创建时验证字段、类型、operator、aggregate、signal、event type 和 capability。

## 2. Rule 对象

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `rule_id` | string | 是 | 无 | Rule ID。同一 Contract 或 Profile 内 MUST 唯一。 |
| `name` | string | 是 | 无 | 小写 snake_case 名称。 |
| `description` | string | 否 | `""` | 人类可读描述。 |
| `enabled` | boolean | 否 | `true` | 是否启用。 |
| `condition` | Condition | 是 | 无 | 触发条件。 |
| `severity` | string | 是 | 无 | `info`、`notice`、`warning`、`critical`、`emergency`。 |
| `category` | string | 否 | 无 | 领域分类。 |
| `delivery_action` | DeliveryAction | 否 | ReturnPolicy 决定 | 覆盖该 Rule 的交付动作。 |
| `debounce` | duration | 否 | 无 | 条件首次满足后必须持续满足的时间。 |
| `cooldown` | duration | 否 | 无 | 触发后抑制重复触发的时间。 |
| `hysteresis` | object | 否 | 无 | 恢复条件和恢复事件策略。 |
| `evidence` | EvidencePolicy | 否 | Provider 默认 | 触发时收集的证据类型。 |
| `labels` | object | 否 | `{}` | Rule 标签。 |
| `metadata` | object | 否 | `{}` | 扩展元数据。 |

## 3. Condition 类型

Condition 的 `type` 固定允许值：

| 类型 | 定义 |
|---|---|
| `all` | 所有子条件为真。 |
| `any` | 任一子条件为真。 |
| `not` | 子条件为假。 |
| `signal` | 判断 Signal 当前值、窗口聚合、变化率、相对变化或文本匹配。 |
| `event` | 判断离散 Event 的存在、数量或字段过滤。 |
| `state` | 判断 Provider 维护的 Contract、Rule 或 Delivery 状态。 |
| `correlation` | 判断多个条件在同一时间窗内的相关关系。 |

## 4. Boolean Condition

### 4.1 `all`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | 必须为 `all`。 |
| `conditions` | array[Condition] | 是 | 子条件。长度 MUST 大于 0。 |

`all` 只有在所有子条件结果为 `true` 时为 `true`。任一子条件结果为 `unknown` 且没有子条件为 `false` 时，整体结果为 `unknown`。

### 4.2 `any`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | 必须为 `any`。 |
| `conditions` | array[Condition] | 是 | 子条件。长度 MUST 大于 0。 |

`any` 在任一子条件为 `true` 时为 `true`。所有子条件为 `false` 时为 `false`。没有 `true` 且至少一个 `unknown` 时为 `unknown`。

### 4.3 `not`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | 必须为 `not`。 |
| `condition` | Condition | 是 | 被取反条件。 |

`not(unknown)` 的结果为 `unknown`。

## 5. Signal Condition

Signal Condition 字段：

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `type` | string | 是 | 无 | 必须为 `signal`。 |
| `subject_ref` | ExAP URI | 否 | Scope 解析结果 | 目标 Subject。省略时 Provider 对适用 Subject 集合求值。 |
| `signal` | string | 是 | 无 | Signal 名称。 |
| `operator` | string | 是 | 无 | Signal operator。 |
| `value` | any | 条件必填 | 无 | 比较值。除 `exists`、`not_exists`、`changed`、`unchanged` 外均 REQUIRED。 |
| `window` | duration | 否 | 无 | 聚合窗口。 |
| `aggregate` | string | 否 | `last` | 聚合函数。 |
| `duration` | duration | 否 | 无 | 条件必须持续成立的时间。 |
| `missing` | string | 否 | `unknown` | 缺失数据语义：`unknown`、`false`、`true`、`error`。 |
| `case_sensitive` | boolean | 否 | `true` | 字符串匹配是否大小写敏感。 |
| `semantic_model_ref` | string | 否 | Provider 默认 | 语义匹配模型引用。 |

### 5.1 Signal operator

| Operator | `value` | 支持类型 | 语义 |
|---|---:|---|---|
| `eq` | 必填 | 任意 | Signal 值等于 value。 |
| `ne` | 必填 | 任意 | Signal 值不等于 value。 |
| `gt` | 必填 | number、datetime、duration | 大于。 |
| `gte` | 必填 | number、datetime、duration | 大于等于。 |
| `lt` | 必填 | number、datetime、duration | 小于。 |
| `lte` | 必填 | number、datetime、duration | 小于等于。 |
| `exists` | 禁止 | 任意 | Signal 在当前评估上下文中存在。 |
| `not_exists` | 禁止 | 任意 | Signal 在当前评估上下文中不存在。 |
| `changed` | 禁止 | 任意 | 当前值相对上一有效值发生变化。 |
| `unchanged` | 禁止 | 任意 | 当前值相对上一有效值未变化。 |
| `regex` | 必填 | string | 正则匹配。 |
| `contains` | 必填 | string、array | 字符串包含或数组包含。 |
| `in` | 必填 | 任意 | Signal 值属于 value 数组。 |
| `not_in` | 必填 | 任意 | Signal 值不属于 value 数组。 |
| `rate_gt` | 必填 | number | 单位时间变化率大于 value。需要 `window`。 |
| `rate_lt` | 必填 | number | 单位时间变化率小于 value。需要 `window`。 |
| `relative_change_gt` | 必填 | number | 相对变化比例大于 value。需要 `window`。 |
| `relative_change_lt` | 必填 | number | 相对变化比例小于 value。需要 `window`。 |
| `relative_drop_gt` | 必填 | number | 相对下降比例大于 value。需要 `window`。 |
| `semantic_match` | 必填 | string 或 array[string] | 语义匹配。Provider capability 的 `semantic_match` MUST 为 true。 |

### 5.2 Aggregate

| Aggregate | 语义 |
|---|---|
| `last` | 最近一个有效值。 |
| `min` | 窗口最小值。 |
| `max` | 窗口最大值。 |
| `avg` | 窗口平均值。 |
| `sum` | 窗口求和。 |
| `count` | 窗口样本数。 |
| `p50`、`p90`、`p95`、`p99` | 窗口分位数。 |
| `delta` | 窗口末值减首值。 |
| `rate` | `delta / window_seconds`。 |

## 6. Event Condition

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `type` | string | 是 | 无 | 必须为 `event`。 |
| `subject_ref` | ExAP URI | 否 | Scope 解析结果 | 目标 Subject。 |
| `event_type` | string | 是 | 无 | Event type。 |
| `operator` | string | 是 | 无 | Event operator。 |
| `value` | any | 条件必填 | 无 | Count、字段值或语义目标。 |
| `window` | duration | 否 | 当前评估时刻 | Event 搜索窗口。 |
| `filters` | array[FieldFilter] | 否 | `[]` | Event 字段过滤条件。 |

Event operator：

| Operator | 语义 |
|---|---|
| `exists` | 窗口内存在至少一个匹配 Event。 |
| `count_eq` | 匹配 Event 数量等于 value。 |
| `count_gt` | 匹配 Event 数量大于 value。 |
| `count_gte` | 匹配 Event 数量大于等于 value。 |
| `count_lt` | 匹配 Event 数量小于 value。 |
| `count_lte` | 匹配 Event 数量小于等于 value。 |
| `field_eq` | 至少一个 Event 的字段过滤结果为真。 |
| `field_regex` | 至少一个 Event 的字段正则匹配。 |
| `field_contains` | 至少一个 Event 的字段包含 value。 |
| `semantic_match` | 至少一个 Event 的字段与语义目标匹配。 |

### 6.1 FieldFilter

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `path` | string | 是 | Event data 中的点路径。 |
| `operator` | string | 是 | `eq`、`ne`、`regex`、`contains`、`in`、`not_in`、`semantic_match`。 |
| `value` | any | 条件必填 | 比较值。 |
| `case_sensitive` | boolean | 否 | 字符串匹配大小写策略。 |

## 7. State Condition

State Condition 判断 Provider 内部状态。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | 必须为 `state`。 |
| `state_path` | string | 是 | 状态路径，例如 `contract.status`。 |
| `operator` | string | 是 | Signal operator。 |
| `value` | any | 条件必填 | 比较值。 |

## 8. Correlation Condition

Correlation Condition 用于多条件窗口相关。

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `type` | string | 是 | 必须为 `correlation`。 |
| `mode` | string | 是 | `all_within_window`、`any_within_window`、`ordered_sequence`。 |
| `within` | duration | 是 | 相关窗口。 |
| `conditions` | array | 是 | 至少两个带 alias 的条件。 |

## 9. Debounce

`debounce` 出现在 Rule 顶层。Rule 条件从 false/unknown 变为 true 后，必须连续保持 true 达到 debounce 时长才触发。期间出现 false 时计时归零。期间出现 unknown 时根据最内层 `missing` 语义处理。

## 10. Hysteresis

`hysteresis.recover_when` 定义恢复条件。Rule 触发后，在恢复条件满足前，同一 Rule 不得重复触发，除非 severity 升级或 cooldown 已结束且 Provider 明确声明允许重复。

`emit_recovery_event=true` 时，Provider 在恢复条件满足时生成 `exap.attention.recovered`。

## 11. Cooldown

`cooldown` 是同一 Rule 成功触发后的抑制窗口。Cooldown 内相同 dedupe key 的重复触发 MUST 被抑制。Severity 升级可突破 cooldown。

## 12. EvidencePolicy

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `include` | array[string] | 是 | 证据类型。允许值见下表。 |
| `max_items` | integer | 否 | 最大证据项数量。 |
| `max_excerpt_chars` | integer | 否 | 文本摘录最大字符数。 |
| `include_subject_attributes` | boolean | 否 | 是否包含 Subject attributes。 |

`include` 允许值：`matched_values`、`window_stats`、`event_excerpt`、`log_excerpt`、`semantic_score`、`subject_snapshot`、`trace_link`、`redaction_report`。

## 13. 缺失值语义

`missing` 允许值：

| 值 | 语义 |
|---|---|
| `unknown` | 条件结果为 unknown。 |
| `false` | 条件结果为 false。 |
| `true` | 条件结果为 true。 |
| `error` | Provider 返回 validation 或 runtime error。 |

## 14. 正则与语义匹配

Regex 使用 Provider capability 声明的正则引擎。Provider MUST 在 capability 中公开正则限制，包括最大 pattern 长度、最大执行时间或拒绝回溯风险模式的策略。

`semantic_match` 是可选能力。Provider capability 的 `rule_capabilities.semantic_match=false` 时，Provider MUST 拒绝包含 `semantic_match` 的 Rule。
