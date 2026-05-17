# 17. MCP and A2A Integration

## 1. 定义

ExAP 与 MCP、A2A 的关系固定如下：

| 协议 | 交互方向 | 主要对象 | ExAP 绑定角色 |
|---|---|---|---|
| MCP | Agent-to-tool/resource | Tools、Resources、Prompts、Notifications、Progress、Cancellation | ExAP Provider 作为 MCP server，暴露 Lifecycle API。 |
| A2A | Agent-to-agent | Agent Card、Task、Message、Part、Artifact、Streaming、Push Notifications | ExAP Provider 作为远程 agent，使用 Task 管理长时间关注。 |
| ExAP | Environment-to-consumer | Attention Contract、Rule、Attention Event、Evidence、PrivacyPolicy | 定义环境感知语义。 |

ExAP Binding 固定 ExAP 对象到 MCP/A2A 主流开发对象的映射，Core 对象语义仍由 ExAP schema、Rule DSL、Capability 和 Lifecycle API 维护。

## 2. MCP Binding

### 2.1 MCP Server 角色

ExAP MCP server 是 MCP Server。Agent runtime 是 MCP Host/Client。ExAP MCP server MUST 通过 MCP tools 暴露 ExAP Lifecycle API。

### 2.2 Tools

ExAP MCP server MUST 至少暴露以下 tools：

| Tool | ExAP method | 输入 | 输出 |
|---|---|---|---|
| `exap_discover` | `exap.discover` | discover params | capability document。 |
| `exap_contract_create` | `exap.contract.create` | contract、validate_only、idempotency_key | contract_id、status、effective_contract。 |
| `exap_wait` | `exap.wait` | contract_id、until、timeout、min_severity、include、cursor | wait result。 |
| `exap_status` | `exap.status` | contract_id、include | compressed state。 |
| `exap_attention_ack` | `exap.attention.ack` | attention_id、action、snooze_for、comment | ack result。 |
| `exap_contract_revoke` | `exap.contract.revoke` | contract_id、reason | revoke result。 |

Tool `inputSchema` 和 `outputSchema` 必须使用 JSON Schema，并引用 lifecycle Params/Result schema。`exap_wait` 描述必须声明长时间阻塞、cursor 恢复、progress/keepalive、return reason enum 和 cancellation 语义。

### 2.3 Resources

ExAP MCP server 暴露以下 resources：

| Resource URI | 内容 |
|---|---|
| `exap://provider/capability/current` | Capability Document。 |
| `exap://contracts/active` | Active Contract 列表。 |
| `exap://attention/recent` | 最近 Attention Event 摘要。 |
| `exap://profiles` | 可用 Domain Profiles。 |

Resources 必须执行 authorization 与 privacy policy，并使用 privacy report/redaction 语义处理受限字段。

### 2.4 Prompts

ExAP MCP server 可暴露 prompts 生成常见 Contract 草案。Prompt output 必须产生或请求结构化 Contract 字段，最终 active Contract 仍经过 Contract schema、Rule DSL schema、capability compatibility 和 privacy validation。

### 2.5 Progress and cancellation

`exap_wait` is a long-running tool. MCP cancellation maps to `interrupted` wait handling or tool-level cancellation. Contract revocation uses explicit `exap_contract_revoke` or an explicit revoke-on-cancel input flag.

### 2.6 Notifications

MCP notifications can announce server capability changes or event availability. Event delivery uses `exap_wait`, stream, or push. If an MCP host surfaces event availability to a model runtime, the next structured call is `exap_status` or `exap_wait`.

## 3. A2A Binding

### 3.1 Agent Card

An ExAP A2A server MUST publish an Agent Card. The Agent Card MUST include:

| Field | Requirement |
|---|---|
| `name` | Identifies the ExAP provider agent. |
| `description` | States supported environment awareness domains. |
| `url` | A2A endpoint. |
| `version` | Provider version. |
| `capabilities.streaming` | true if streaming is supported. |
| `capabilities.pushNotifications` | true if push notification is supported. |
| `skills` | At least `create_attention_contract` and `wait_for_attention`. |
| `defaultInputModes` | MUST include `application/json`. |
| `defaultOutputModes` | MUST include `application/exap+json`. |
| `securitySchemes` | Authentication requirements. |

### 3.2 Task mapping

| ExAP operation | A2A representation |
|---|---|
| Create Contract | A2A Task that returns an ExAP Contract Artifact. |
| Wait | A2A Task that remains working until Attention Event or terminal state. |
| Attention Event | Artifact with media type `application/exap+json`. |
| Ack | Message or Task update referencing the attention artifact. |
| Revoke | Message or Task that moves Contract to revoked. |

A2A Task terminal states MUST be mapped to ExAP states:

| A2A state | ExAP state or return reason |
|---|---|
| `completed` | `completed`。 |
| `failed` | `provider_error` or `failed`。 |
| `canceled` | `interrupted` or `revoked` depending on request. |
| `input-required` | Consumer action required; ExAP Contract remains active unless policy says otherwise. |
| `auth-required` | Authorization incomplete; Contract MUST NOT become active. |

### 3.3 Message and Part mapping

A2A Message Part with `data` carries Contract JSON, wait params, ack params, revoke params, or validate-only draft requests. A2A Artifact Part with `data` carries ExAP Attention Event JSON when media type is `application/exap+json`.

### 3.4 Streaming and push

A2A SSE streaming maps to ExAP stream. A2A push notifications map to ExAP push. A2A streaming updates MAY include current Task status, but the canonical environment event remains the ExAP Attention Event Artifact.

### 3.5 Opaque execution

A2A remote agents do not expose internal tools or memory. ExAP A2A Provider MUST expose capability, Contract status, Attention Events and audit-compatible summaries; it MUST NOT expose hidden chain-of-thought, internal prompts, private tools or proprietary decision logic.

### 3.6 Natural language draft flow

`text/plain` intent maps to a validate-only draft flow:

1. Provider resolves scope, candidate subjects, proposed rules, delivery changes and privacy/evidence changes.
2. Provider returns `validate_only=true` draft output with required confirmations.
3. Consumer sends structured `application/json` ContractCreateParams for active creation.

Natural language input creates drafts and confirmation requests; active Contract creation uses structured JSON.

## 4. Combined MCP + A2A deployment

A deployment may expose both:

```text
Agent Host --MCP--> ExAP tool server --observes--> Environment
Agent A --A2A--> ExAP awareness agent --observes--> Environment
```

When both bindings are present, Contract IDs, Attention IDs and PrivacyPolicy semantics MUST be identical across bindings.

## 5. Mainstream agent development pattern

Agent developers use ExAP through this fixed pattern:

1. Discover provider capability.
2. Create Contract with explicit scope、rules、delivery、privacy。
3. Call blocking wait for long-running or external events。
4. Receive Attention Event with compact evidence。
5. Fetch more context only after event triggers。
6. Ack when required。
7. Revoke when done。

This pattern eliminates fixed-interval polling at the agent level while preserving explicit user and provider control.
