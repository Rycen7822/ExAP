# 08. Transport Bindings

## 1. 定义

Transport Binding 将 Lifecycle API、Attention Event 和 Capability Document 映射到具体传输。Binding MUST 保持 Core 对象语义不变。

## 2. Content Mode

| Mode | 定义 |
|---|---|
| `structured` | 事件整体作为 JSON 对象传输。 |
| `binary` | Envelope 元数据放入 header 或 frame metadata，data 单独传输。 |

ExAP v0.2 的示例和 schema 使用 structured mode。

## 3. HTTP Binding

### 3.1 Endpoints

| Method | Path | ExAP method |
|---|---|---|
| `GET` | `/exap/capability` | `exap.discover` |
| `POST` | `/exap/contracts` | `exap.contract.create` |
| `GET` | `/exap/contracts/{contract_id}` | `exap.contract.get` |
| `GET` | `/exap/contracts` | `exap.contract.list` |
| `PATCH` | `/exap/contracts/{contract_id}` | `exap.contract.update` |
| `POST` | `/exap/contracts/{contract_id}/pause` | `exap.contract.pause` |
| `POST` | `/exap/contracts/{contract_id}/resume` | `exap.contract.resume` |
| `DELETE` | `/exap/contracts/{contract_id}` | `exap.contract.revoke` |
| `POST` | `/exap/contracts/{contract_id}/wait` | `exap.wait` |
| `GET` | `/exap/contracts/{contract_id}/stream` | `exap.stream.open` |
| `POST` | `/exap/attention/{attention_id}/ack` | `exap.attention.ack` |
| `GET` | `/exap/contracts/{contract_id}/status` | `exap.status` |
| `POST` | `/exap/observations/query` | `exap.observation.query` |

### 3.2 Headers

| Header | 必填 | 定义 |
|---|---:|---|
| `Content-Type` | 请求体存在时是 | `application/json`。 |
| `ExAP-Version` | 是 | ExAP 版本。 |
| `ExAP-Request-Id` | 否 | 请求 ID。 |
| `ExAP-Trace-Id` | 否 | Trace ID。 |
| `Authorization` | 远程 Provider 是 | 凭据。 |

### 3.3 HTTP 状态码

| 状态码 | ExAP 错误 |
|---:|---|
| `200` | 成功。 |
| `201` | Contract 创建成功。 |
| `202` | 请求已接受，异步处理。 |
| `400` | `ExAP-4000` 至 `ExAP-4007`。 |
| `401` | `ExAP-4010`。 |
| `403` | `ExAP-4030`、`ExAP-4031`。 |
| `404` | `ExAP-4040`。 |
| `409` | `ExAP-4090`。 |
| `413` | `ExAP-4130`。 |
| `429` | `ExAP-4290`。 |
| `500` | `ExAP-5000`。 |
| `503` | `ExAP-5030`。 |
| `504` | `ExAP-5040`。 |

## 4. Webhook Binding

Webhook 用于 `push`。Provider 向 Consumer endpoint 发送 structured Attention Event。

要求：

- HTTP method MUST 为 `POST`。
- Body MUST 是 Attention Event JSON。
- Provider MUST 支持 HMAC、Bearer token、mTLS 或等价认证中的至少一种。
- Consumer 以 `2xx` 表示成功。
- 非 `2xx` 根据 Contract retry 策略处理。
- Provider MUST 包含 `ExAP-Event-Id` 和 `ExAP-Timestamp`。

签名 header：

| Header | 定义 |
|---|---|
| `ExAP-Signature` | 签名值。 |
| `ExAP-Signature-Alg` | 算法，例如 `hmac-sha256`。 |
| `ExAP-Timestamp` | 发送时间。 |
| `ExAP-Event-Id` | Event ID。 |

## 5. SSE Binding

SSE 用于 `stream`。

Endpoint：

```text
GET /exap/contracts/{contract_id}/stream?min_severity=info&cursor=...
```

SSE event 名称：`exap.attention.triggered`、`exap.attention.recovered`、`exap.attention.summary`、`exap.contract.state_changed`、`exap.keepalive`、`exap.error`。

每个 `data` 帧 MUST 是 JSON。Provider MUST 定期发送 keepalive，间隔由 capability 声明或默认为 `PT30S`。

## 6. WebSocket Binding

连接后 Consumer MUST 发送：

```json
{"type":"exap.stream.subscribe","contract_id":"act_process_wait_001","min_severity":"info","cursor":null}
```

Provider 返回 JSON object。每条消息 MUST 包含 `type` 字段。Provider MUST 在正常关闭前发送 `exap.stream.closed`。网络异常关闭时该消息不保证出现。

## 7. MQTT Binding

Topic 格式：

```text
exap/v0/<authority>/<environment_id>/<subject_type>/<subject_id>/attention
```

Payload MUST 是 UTF-8 JSON。Emergency severity event MUST 使用 QoS 1 或 QoS 2，除非 capability 明确声明只支持 QoS 0。

Contract 管理 MAY 通过 HTTP、本地 API 或 MQTT request/reply topic 完成。若使用 MQTT request/reply，topic 格式：

```text
exap/v0/<authority>/commands/<consumer_id>/request
exap/v0/<authority>/commands/<consumer_id>/reply
```

## 8. NATS Binding

NATS subject 格式：

```text
exap.v0.<authority>.<environment>.<subject_type>.<subject_id>.attention
```

Provider MUST 在 capability 中声明是否支持 JetStream 持久化和 replay。

## 9. Kafka Binding

Kafka topic：

| Topic | 内容 |
|---|---|
| `exap.attention.events` | Attention Event。 |
| `exap.contract.audit` | Contract lifecycle audit。 |
| `exap.observations.raw` | 受权限控制的 Observation。 |

Kafka key MUST 包含 `contract_id` 或 `subject_ref`，以保持相关事件分区一致。

## 10. Local Binding

Local binding 支持：

| Transport | 定义 |
|---|---|
| `local_stdio` | 本地进程标准输入输出。 |
| `local_socket` | Unix domain socket 或 named pipe。 |

Local binding MUST 使用 JSON-RPC 2.0 message。Local Provider MUST 明确记录数据目录、日志目录和进程权限。

## 11. MCP Binding

MCP binding 将 Lifecycle API 暴露为 MCP tools，并可用 resources 暴露 capability、active contracts 和 recent attention events。详细要求见 `17-mcp-a2a-integration.md`。

## 12. A2A Binding

A2A binding 将 ExAP Provider 表示为远程 agent。Contract 创建和 wait 可作为 A2A Task，Attention Event 可作为 Artifact。详细要求见 `17-mcp-a2a-integration.md`。

## 13. 传输安全要求

- 远程传输 MUST 使用 TLS 或等价安全通道。
- Webhook、SSE、WebSocket、MQTT、NATS、Kafka 绑定 MUST 有认证机制。
- Provider MUST 对 replay、重复交付、签名过期和 payload 超限执行防护。
- Authorization header、token、secret MUST NOT 出现在 Attention Event payload 或 evidence 中。
