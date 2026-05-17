# 16. Standards Compatibility

## 1. 定义

ExAP 是 attention contract 层。现有标准继续承担 envelope、消息传输、遥测采集、授权、agent-to-tool 和 agent-to-agent 通信职责。

## 2. CloudEvents

CloudEvents 统一事件 envelope。ExAP Attention Event 使用 CloudEvents-compatible structured JSON。

| ExAP | CloudEvents |
|---|---|
| Attention Event | CloudEvent。 |
| `id` | Event ID。 |
| `source` | Provider source。 |
| `type` | ExAP event type。 |
| `subject` | 主 Subject。 |
| `time` | 生成时间。 |
| `data` | ExAP AttentionData。 |

Reference：

- https://cloudevents.io/
- https://github.com/cloudevents/spec

## 3. AsyncAPI

AsyncAPI 描述 message-driven API。ExAP Provider 使用 MQTT、Kafka、NATS、WebSocket 或 webhook 时，MAY 发布 AsyncAPI 文档描述 channels、messages、operations 和 bindings。

| ExAP | AsyncAPI |
|---|---|
| Provider API | AsyncAPI document。 |
| Attention stream | Channel。 |
| Attention Event | Message。 |
| Transport binding | Binding。 |
| Schemas | Components schemas。 |

Reference：

- https://www.asyncapi.com/docs/reference/specification/latest

## 4. OpenTelemetry

OpenTelemetry 可作为 Signal、Observation、Evidence 的来源。ExAP 不要求 Provider 使用 OpenTelemetry。

| OpenTelemetry | ExAP |
|---|---|
| Metric datapoint | Observation。 |
| Log record | Event 或 Evidence。 |
| Trace/span | TraceContext 或 trace_link evidence。 |
| Resource attributes | Subject attributes。 |
| Semantic convention | Signal 命名参考。 |

Reference：

- https://opentelemetry.io/docs/concepts/signals/

## 5. JSON Schema

ExAP schemas 使用 JSON Schema Draft 2020-12。所有跨 schema 引用使用 canonical `$id`。

Reference：

- https://json-schema.org/draft/2020-12

## 6. MQTT

MQTT 作为 IoT 和边缘设备 transport。ExAP MQTT Binding 定义 topic 和 payload 语义，不改变 MQTT QoS、retain、session 等机制。

Reference：

- https://mqtt.org/

## 7. NATS

NATS 使用 subject-based pub/sub。ExAP NATS Binding 将 authority、environment、subject 和 attention 映射到 NATS subject。

Reference：

- https://docs.nats.io/nats-concepts/core-nats/pubsub
- https://docs.nats.io/nats-concepts/subjects

## 8. OAuth 2.0

OAuth 2.0 可用于远程 Provider 授权。ExAP scope 可映射为 OAuth scope。

ExAP scope 示例：

```text
exap.contract.create
exap.contract.read
exap.contract.revoke
exap.attention.receive
exap.attention.ack
exap.subject.mailbox.read_metadata
exap.subject.mailbox.read_summary
exap.subject.process.read_metrics
```

Reference：

- https://datatracker.ietf.org/doc/html/rfc6749

## 9. MCP

MCP 负责 agent-to-tool 和 agent-to-resource 通信。ExAP Provider 作为 MCP server 时，Lifecycle API 映射为 MCP tools，capability 和 recent events 映射为 MCP resources。MCP Binding 不改变 ExAP Contract 和 Attention Event schema。

Reference：

- https://modelcontextprotocol.io/specification/2025-11-25
- https://modelcontextprotocol.io/docs/learn/architecture

## 10. A2A

A2A 负责 agent-to-agent 通信、Agent Card discovery、Task、Message、Part、Artifact、streaming 和 push notification。ExAP Provider 作为 A2A remote agent 时，Contract 创建和 wait 表示为 Task，Attention Event 表示为 `application/exap+json` Artifact。

Reference：

- https://a2a-protocol.org/latest/
- https://a2a-protocol.org/latest/topics/key-concepts/
- https://a2a-protocol.org/latest/topics/streaming-and-async/

## 11. 兼容性原则

1. ExAP Core 对 transport 保持中立。
2. ExAP Attention Event 可作为 CloudEvents structured event。
3. ExAP Provider 可用 AsyncAPI、OpenAPI 或 MCP 描述接口。
4. ExAP 可消费 OpenTelemetry 数据，但不依赖 OpenTelemetry。
5. ExAP 可被 A2A agent 使用，但不替代 A2A task lifecycle。
6. ExAP 权限模型必须能表达 scope、consent、redaction、retention 和 audit。
