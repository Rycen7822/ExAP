# 07. Lifecycle API

## 1. 定义

Lifecycle API 是 EAP 的通用操作集合。所有绑定必须保持这些 method 的语义一致。JSON-RPC 2.0 表示法用于规范方法名、参数和响应；HTTP、MCP、A2A 等绑定可将这些方法映射到 endpoint、tool 或 task。

## 2. 通用请求格式

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "method": "eap.contract.create",
  "params": {}
}
```

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `jsonrpc` | string | 是 | 必须为 `2.0`。 |
| `id` | string/integer | 是 | 请求 ID。 |
| `method` | string | 是 | EAP method。 |
| `params` | object | 是 | method 参数。 |

## 3. 通用响应格式

成功：

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "result": {}
}
```

失败：

```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "error": {
    "code": "EAP-4001",
    "message": "Unsupported signal",
    "details": {}
  }
}
```

## 4. 错误码

| Code | 定义 |
|---|---|
| `EAP-4000` | 请求结构无效。 |
| `EAP-4001` | Contract schema 无效。 |
| `EAP-4002` | 不支持的 EAP 版本。 |
| `EAP-4003` | 不支持的 subject type。 |
| `EAP-4004` | 不支持的 signal。 |
| `EAP-4005` | 不支持的 event type。 |
| `EAP-4006` | 不支持的 operator 或 aggregate。 |
| `EAP-4007` | Rule 语义无效。 |
| `EAP-4010` | 未认证。 |
| `EAP-4030` | 授权不足。 |
| `EAP-4031` | Privacy policy 冲突。 |
| `EAP-4040` | Contract、Attention Event 或 Subject 不存在。 |
| `EAP-4090` | 状态冲突。 |
| `EAP-4130` | Payload 超限。 |
| `EAP-4290` | 速率限制。 |
| `EAP-5000` | Provider 内部错误。 |
| `EAP-5030` | Provider 不可用。 |
| `EAP-5040` | Wait 超时。 |

## 5. `eap.discover`

参数见 `06-capability-discovery.md`。

返回：

| 字段 | 类型 | 定义 |
|---|---:|---|
| `capability` | Capability Document | Provider 能力。 |

## 6. `eap.contract.create`

### 6.1 请求参数

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `contract` | Attention Contract | 是 | 无 | 待创建 Contract。 |
| `validate_only` | boolean | 否 | `false` | 只校验不激活。 |
| `idempotency_key` | string | 否 | 无 | 幂等键。 |

### 6.2 响应字段

| 字段 | 类型 | 定义 |
|---|---:|---|
| `contract_id` | string | Contract ID。 |
| `status` | string | `draft` 或 `active`。 |
| `effective_contract` | Attention Contract | Provider 填充默认值后的 Contract。 |
| `warnings` | array[object] | 非阻断警告。 |

Provider MUST 先执行 schema、capability、authorization、privacy、rule uniqueness 校验。校验失败 MUST NOT 创建 Contract。

## 7. `eap.contract.get`

参数：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `contract_id` | string | 是 | Contract ID。 |
| `include_state` | boolean | 否 | 是否包含状态摘要。 |

返回：`contract` 与可选 `state`。

## 8. `eap.contract.list`

参数：

| 字段 | 类型 | 定义 |
|---|---:|---|
| `consumer_id` | string | 限定 Consumer。 |
| `status` | array[string] | 限定状态。 |
| `limit` | integer | 返回数量上限。 |
| `cursor` | string | 分页游标。 |

返回：`contracts`、`next_cursor`。

## 9. `eap.contract.update`

参数：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `contract_id` | string | 是 | Contract ID。 |
| `patch` | object | 是 | JSON merge patch。 |
| `expected_version` | string | 否 | 乐观并发版本。 |

Provider MUST 对更新后的 Contract 重新执行完整校验。终态 Contract MUST NOT 被更新。

## 10. `eap.contract.pause` / `eap.contract.resume`

`pause` 参数：`contract_id`、`reason`。  
`resume` 参数：`contract_id`、`reason`。

暂停后 Provider MUST 停止交付新 Attention Event，但 MAY 继续记录内部 Observation，前提是 PrivacyPolicy 允许。

## 11. `eap.contract.revoke`

参数：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `contract_id` | string | 是 | Contract ID。 |
| `reason` | string | 是 | 撤销原因。 |

Provider MUST 停止观察、停止交付、释放资源，并将状态置为 `revoked`。

## 12. `eap.wait`

参数：

| 字段 | 类型 | 必填 | 默认值 | 定义 |
|---|---:|---:|---|---|
| `contract_id` | string | 是 | 无 | Contract ID。 |
| `until` | array[string] | 是 | 无 | 返回原因集合。 |
| `timeout` | duration | 是 | 无 | 最大阻塞时长。 |
| `min_severity` | string | 否 | `info` | 最低交付 severity。 |
| `include` | array[string] | 否 | `['event']` | 返回内容：`event`、`state`、`summary`。 |
| `cursor` | string | 否 | 无 | 从某事件后继续等待。 |

`until` 允许值：`attention`、`summary`、`completed`、`revoked`、`expired`、`timeout`、`provider_error`、`interrupted`。

返回：

| 字段 | 类型 | 定义 |
|---|---:|---|
| `contract_id` | string | Contract ID。 |
| `return_reason` | string | 返回原因。 |
| `status` | string | Contract 状态。 |
| `event` | Attention Event | `return_reason=attention` 或 `summary` 时存在。 |
| `state` | object | 请求 include 包含 `state` 时存在。 |
| `cursor` | string | 下次 wait 起点。 |

Wait 语义：

- Provider MUST 在 `timeout` 前保持请求打开，除非 `until` 中的原因发生。
- `timeout` 发生时 Provider MUST NOT 自动撤销 Contract。
- Consumer 新请求或上层取消导致 wait 中断时，Provider 返回 `interrupted` 或绑定层取消响应。
- 多个 wait 同时存在时，Provider MUST 保证每个 wait 根据相同 Contract 状态独立返回。

## 13. `eap.stream.open`

参数：`contract_id`、`min_severity`、`cursor`、`include`。返回流式事件。绑定层定义事件帧格式。

## 14. `eap.attention.ack`

参数：

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `attention_id` | string | 是 | Attention ID。 |
| `action` | string | 是 | `seen`、`snooze`、`dismiss`、`escalate`。 |
| `actor` | string | 否 | 执行动作者。 |
| `snooze_for` | duration | 条件必填 | `action=snooze` 时 REQUIRED。 |
| `comment` | string | 否 | 说明。 |

## 15. `eap.status`

参数：`contract_id`、`include`。返回压缩状态，不返回完整原始观测流。Consumer MUST NOT 用短间隔 `eap.status` 代替 `eap.wait`。

## 16. `eap.observation.query`

用于受控查询 Observation。Provider MUST 进行权限、privacy、retention 检查。查询结果 MUST 受 payload limits 限制。
