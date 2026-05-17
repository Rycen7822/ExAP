# EAP 手册目录

## 规范性关键词

本文档使用以下关键词，含义固定：

| 关键词 | 含义 |
|---|---|
| MUST | 强制要求。不满足即不符合规范。 |
| MUST NOT | 强制禁止。出现即不符合规范。 |
| REQUIRED | 必填或强制存在。 |
| OPTIONAL | 可省略。省略时适用该字段定义的默认值。 |
| MAY | 协议允许的可选能力。使用方不得假定所有实现均支持。 |

本文档不使用未定义的自然语言条件作为协议要求。表格中的默认值、允许值、状态机和错误码构成规范的一部分。

## 阅读顺序

| 顺序 | 文件 | 内容 |
|---:|---|---|
| 1 | `01-overview-and-scope.md` | 协议目标、非目标、角色、工作流。 |
| 2 | `02-core-model.md` | Environment、Subject、Signal、Observation、Event、Contract、Attention Event。 |
| 3 | `03-attention-contract.md` | Attention Contract 的全部字段。 |
| 4 | `04-rule-dsl.md` | Rule DSL、Condition、operator、窗口、冷却、恢复。 |
| 5 | `05-attention-event.md` | CloudEvents-compatible Attention Event 与 Evidence。 |
| 6 | `06-capability-discovery.md` | Provider capability document。 |
| 7 | `07-lifecycle-api.md` | Lifecycle API 请求、响应、错误、状态。 |
| 8 | `08-transport-bindings.md` | HTTP、Webhook、SSE、WebSocket、MQTT、NATS、Kafka、Local。 |
| 9 | `09-privacy-security.md` | 权限、隐私、脱敏、保留、审计、威胁模型。 |
| 10 | `10-domain-profiles.md` | 领域 profile 格式。 |
| 11 | `11-provider-development-guide.md` | Provider 实现要求。 |
| 12 | `12-consumer-and-agent-guide.md` | Consumer 与 agent 对接要求。 |
| 13 | `13-conformance.md` | 一致性等级和测试项。 |
| 14 | `14-reference-implementation.md` | 参考实现结构。 |
| 15 | `15-operations.md` | 运维、限流、事件风暴、租户。 |
| 16 | `16-standards-compatibility.md` | 与现有标准的兼容关系。 |
| 17 | `17-mcp-a2a-integration.md` | MCP 和 A2A 对接方式。 |

## 文件命名规则

- Core 文档使用两位序号前缀。
- Schema 文件使用 `eap-*.schema.json`。
- Profile 文件使用 `*.eap.json`。
- 示例文件使用两位序号前缀。
