# 07. Lifecycle API

## 1. 定义

Lifecycle API 是 ExAP 的通用操作集合。所有绑定必须保持 method、params、result、error 与 state transition 语义一致。JSON-RPC 2.0 envelope 用于规范方法名、请求 ID、成功响应和错误响应；HTTP、MCP、A2A、Local 等绑定将这些方法映射到 endpoint、tool、task 或本地进程调用。

## 2. 通用请求格式

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "method": "exap.contract.create",
  "params": {}
}
```

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `jsonrpc` | string | 是 | 固定为 `2.0`。 |
| `id` | string/integer | 是 | 请求 ID。 |
| `method` | string | 是 | ExAP method。 |
| `params` | object | 是 | method-specific 参数对象。 |

Schema `schemas/exap-lifecycle-message.schema.json` 使用 method-discriminated `oneOf`：每个 method 都有独立 Request schema 和独立 Params schema。未知 params 字段由 schema 拒绝。

## 3. 通用响应格式

成功响应：

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "result": {
    "contract_id": "act_train_001",
    "status": "active"
  }
}
```

错误响应：

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "exap_code": "ExAP-4004",
      "field": "params.contract.rules[0].condition.signal"
    }
  }
}
```

`error.code` 使用 JSON-RPC-compatible integer code。ExAP 专用错误码放在 `error.data.exap_code`。绑定到 MCP 或 A2A 时沿用同一 envelope 语义。

## 4. 错误码

| JSON-RPC code | `data.exap_code` | 定义 |
|---:|---|---|
| `-32600` | `ExAP-4000` | 请求结构无效。 |
| `-32602` | `ExAP-4001` | Contract schema 无效。 |
| `-32602` | `ExAP-4002` | 不支持的 ExAP 版本。 |
| `-32602` | `ExAP-4003` | 不支持的 subject type。 |
| `-32602` | `ExAP-4004` | 不支持的 signal。 |
| `-32602` | `ExAP-4005` | 不支持的 event type。 |
| `-32602` | `ExAP-4006` | 不支持的 operator 或 aggregate。 |
| `-32602` | `ExAP-4007` | Rule 语义无效。 |
| `-32001` | `ExAP-4010` | 未认证。 |
| `-32003` | `ExAP-4030` | 授权不足。 |
| `-32003` | `ExAP-4031` | Privacy policy 冲突。 |
| `-32004` | `ExAP-4040` | Contract、Attention Event 或 Subject 不存在。 |
| `-32009` | `ExAP-4090` | 状态冲突。 |
| `-32013` | `ExAP-4130` | Payload 超限。 |
| `-32029` | `ExAP-4290` | 速率限制。 |
| `-32000` | `ExAP-5000` | Provider 内部错误。 |
| `-32030` | `ExAP-5030` | Provider 不可用。 |
| `-32040` | `ExAP-5040` | Wait 超时。 |

## 5. Method-specific params 与 result

| Method | Params schema | Result schema |
|---|---|---|
| `exap.discover` | `DiscoverParams` | `DiscoverResult` |
| `exap.contract.create` | `ContractCreateParams` | `ContractCreateResult` |
| `exap.contract.get` | `ContractGetParams` | `ContractGetResult` |
| `exap.contract.list` | `ContractListParams` | `ContractListResult` |
| `exap.contract.update` | `ContractUpdateParams` | `ContractUpdateResult` |
| `exap.contract.pause` | `ContractPauseParams` | `ContractPauseResult` |
| `exap.contract.resume` | `ContractResumeParams` | `ContractResumeResult` |
| `exap.contract.revoke` | `ContractRevokeParams` | `ContractRevokeResult` |
| `exap.wait` | `WaitParams` | `WaitResult` |
| `exap.stream.open` | `StreamOpenParams` | `StreamOpenResult` |
| `exap.attention.ack` | `AttentionAckParams` | `AttentionAckResult` |
| `exap.status` | `StatusParams` | `StatusResult` |
| `exap.observation.query` | `ObservationQueryParams` | `ObservationQueryResult` |

Generic `Response.result` remains an object envelope. Implementations must validate result bodies against the method-specific Result schema for the request method.

## 6. `exap.discover`

参数字段：

| 字段 | 类型 | 定义 |
|---|---:|---|
| `environment_ref` | ExAP URI | 限定 Environment。 |
| `subject_types` | array[string] | 限定 Subject type。 |
| `profile_ids` | array[string] | 限定返回的 profile。 |

返回 `capability`，其值为 Capability Document。

## 7. `exap.contract.create`

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `contract` | Attention Contract | 是 | 无 | 待创建 Contract。 |
| `validate_only` | boolean | 否 | `false` | 只校验并返回 effective contract。 |
| `idempotency_key` | string | 否 | 无 | 幂等键。 |

Provider 必须先执行 schema、capability、authorization、privacy、rule uniqueness 和 delivery compatibility 校验。`validate_only=true` 返回校验结果与 effective contract，并保持 provider state 不变。

## 8. Contract state methods

`exap.contract.get` 使用 `contract_id` 与可选 `include_state`。
`exap.contract.list` 支持 `consumer_id`、`status`、`limit`、`cursor`。
`exap.contract.update` 使用 `contract_id`、`patch`、可选 `expected_version`，更新后的 Contract 必须重新完成完整校验。
`exap.contract.pause` 与 `exap.contract.resume` 使用 `contract_id`、`reason`。
`exap.contract.revoke` 使用 `contract_id`、`reason`，Provider 必须停止观察、停止交付、释放资源，并将状态置为 `revoked`。

## 9. `exap.wait`

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `contract_id` | string | 是 | 无 | Contract ID。 |
| `until` | array[ReturnReason] | 是 | 无 | 返回原因集合。 |
| `timeout` | Duration | 是 | 无 | 最大阻塞时长。 |
| `min_severity` | Severity | 否 | `info` | 最低交付 severity。 |
| `include` | array[`event`,`state`,`summary`] | 否 | `event` | 返回内容集合。 |
| `cursor` | string | 否 | 无 | 从某事件后继续等待。 |

`until` 允许：`attention`、`summary`、`completed`、`revoked`、`expired`、`timeout`、`provider_error`、`interrupted`。`timeout` 与 `snooze_for` 使用 shared `Duration` schema。

Wait 语义：

- Provider 在 `timeout` 前保持请求打开，直到 `until` 中的原因发生。
- `timeout` 返回 `return_reason=timeout`，Contract 状态保持由生命周期规则决定。
- Consumer 新请求或上层取消导致 wait 中断时，Provider 返回 `interrupted` 或绑定层取消响应。
- MCP tool cancellation 映射为 `interrupted` 或 tool-level cancellation；只有显式 `revoke` 请求会撤销 Contract。
- 多个 wait 同时存在时，Provider 必须保证每个 wait 根据相同 Contract 状态独立返回。

## 10. `exap.stream.open`

参数：`contract_id`、`min_severity`、`cursor`、`include`。返回 `stream_id`、`contract_id`、`status` 和可选 `cursor`。绑定层定义事件帧格式、keepalive、error frame 与恢复语义。

## 11. `exap.attention.ack`

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `attention_id` | string | 是 | Attention ID。 |
| `action` | `seen`/`snooze`/`dismiss`/`escalate` | 是 | Ack 动作。 |
| `actor` | string | 否 | 执行动作者。 |
| `snooze_for` | Duration | 条件必填 | `action=snooze` 时必填；其他 action 禁止携带。 |
| `comment` | string | 否 | 说明。 |

返回 `attention_id`、`action`、`status`。

## 12. `exap.status` 与 `exap.observation.query`

`exap.status` 使用 `contract_id` 与可选 `include`，返回压缩状态、`recent_events`、delivery 或 metrics 子集。Consumer 以 `exap.wait`、stream 或 push 作为主要事件交付路径。

`exap.observation.query` 用于受控查询 Observation。Provider 必须执行 authorization、privacy、retention、pagination 和 payload limits。
