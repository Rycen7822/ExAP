# 01. ExAP 概览与范围

## 1. 协议目标

ExAP 的目标是统一各类环境变化的主动感知接口。ExAP 定义 Consumer 如何声明关注意图，Provider 如何声明感知能力，Rule 如何被评估，Attention Event 如何被交付，隐私和授权如何绑定到每个 Contract。

ExAP 覆盖以下场景：

| 场景 | Subject 示例 | Signal / Event 示例 |
|---|---|---|
| 邮件 | `mailbox`、`email_thread` | `mail.message.received`、`mail.content.semantic_intent` |
| 本地进程 | `process`、`process_group` | `process.status`、`process.cpu.percent` |
| GPU/硬件 | `gpu`、`disk` | `gpu.util.percent`、`disk.free_gb` |
| 文件 | `file`、`directory` | `file.exists`、`file.modified_at` |
| 日历 | `calendar`、`calendar_event` | `calendar.event.starts_in_minutes` |
| IoT | `iot_device`、`sensor` | `device.temperature_c`、`device.alert` |
| CI/CD | `pipeline`、`job`、`artifact` | `ci.job.failed`、`artifact.created` |
| Agent 协作 | `agent_task`、`artifact` | `task.status.changed` |

## 2. 非目标

ExAP MUST NOT 被实现为以下系统的替代品：

| 非目标 | 边界 |
|---|---|
| 通用消息总线 | MQTT、NATS、Kafka、Webhook 等传输仍由对应系统提供。 |
| 遥测采集系统 | OpenTelemetry、系统 API、SaaS API、传感器仍负责采集。 |
| Agent 工具协议 | MCP 负责 agent-to-tool；ExAP 只提供 awareness contract 语义。 |
| Agent 协作协议 | A2A 负责 agent-to-agent；ExAP 只提供环境感知对象和事件。 |
| 认证授权标准 | OAuth、mTLS、API key、企业 IAM 仍负责认证授权。 |
| 自动决策引擎 | ExAP 只判断是否需要注意，不规定 Consumer 的最终业务动作。 |

## 3. 系统角色

### 3.1 Consumer

Consumer 是创建 Contract 并接收 Attention Event 的实体。Consumer 类型固定为：

| 类型 | 定义 |
|---|---|
| `agent` | LLM agent 或自动推理系统。 |
| `application` | 桌面、移动、Web 或服务端应用。 |
| `service` | 后台服务或平台组件。 |
| `user_interface` | 用于呈现提醒或状态的 UI。 |
| `automation` | 自动化脚本、工作流或调度器。 |
| `human_proxy` | 代表人工用户接收和确认事件的系统。 |
| `custom` | Provider capability 中明确定义的扩展类型。 |

Consumer MUST 校验 Provider capability 后再创建 Contract。Consumer MUST 在不再需要关注时撤销 Contract。

### 3.2 Provider

Provider 是观察环境、评估规则并交付事件的实体。Provider 类型固定为：

| 类型 | 定义 |
|---|---|
| `local_daemon` | 本地守护进程。 |
| `connector` | SaaS、邮件、日历、Git、工单等连接器。 |
| `monitoring_service` | 监控平台或遥测服务。 |
| `broker` | 事件聚合或路由组件。 |
| `iot_gateway` | IoT 网关或边缘设备管理器。 |
| `cloud_service` | 云平台服务。 |
| `agent_runtime` | Agent runtime 或 agent orchestration 服务。 |
| `custom` | Capability 中定义的扩展类型。 |

Provider MUST 发布 capability document。Provider MUST 拒绝超出 capability、授权或 privacy policy 的 Contract。

### 3.3 Broker

Broker 转发或聚合 Provider 与 Consumer 之间的 ExAP 消息。Broker MUST NOT 改变 Rule 语义、Evidence 内容或 Privacy Report。Broker 进行脱敏时 MUST 在 Privacy Report 中增加脱敏记录。

### 3.4 Subject Owner

Subject Owner 是被观察对象的所有者或控制者。Provider 在涉及敏感 subject 时 MUST 绑定授权、consent 或组织策略。

## 4. 核心工作流

### 4.1 Capability Discovery

Consumer 调用 `exap.discover`，Provider 返回 capability document。Capability document MUST 包含：Provider 身份、ExAP 版本、Subject 类型、Signal、Event 类型、Rule 能力、Delivery 能力、Privacy 能力和限制。

### 4.2 Contract Creation

Consumer 创建 Attention Contract。Provider 必须完成以下验证：

1. Schema 校验。
2. ExAP 版本校验。
3. Scope 权限校验。
4. Subject 解析。
5. Signal 和 Event 支持校验。
6. Operator 和 aggregate 支持校验。
7. Delivery mode 和 transport 支持校验。
8. Privacy policy 校验。
9. Rule ID 唯一性校验。

验证通过后，Contract 状态变为 `active`，除非请求声明 `validate_only=true`。

### 4.3 Wait / Stream / Push

ExAP 支持四种交付模式：

| Mode | 定义 |
|---|---|
| `blocking_wait` | Consumer 调用 `exap.wait` 后，Provider 阻塞到事件、summary、completed、expired、revoked、timeout、interrupted 或 provider_error。 |
| `push` | Provider 主动向 Consumer endpoint 推送 Attention Event。 |
| `stream` | Consumer 建立流式连接，Provider 发送事件、summary、keepalive 和 error。 |
| `pull_with_state_compression` | Consumer 拉取压缩状态，Provider 不返回原始观测流。 |

### 4.4 Ack

Contract 的 `delivery.ack.required=true` 或事件 `delivery.requires_ack=true` 时，Consumer MUST 对事件执行 `exap.attention.ack`。Ack 动作包括 `seen`、`snooze`、`dismiss`、`escalate`。

## 5. 主动感知定义

ExAP 中的主动感知是：Consumer 声明关注意图后，Provider 在后台观察环境，并且只在 Attention Contract 的 Return Policy 要求交付时返回事件。

Provider 内部 MAY 轮询底层系统。Consumer 侧 MUST NOT 为同一关注目标进行短间隔机械轮询来替代 `exap.wait`、stream 或 push。

## 6. 通用性要求

ExAP Core 对具体领域保持中立：

- Core 不硬编码邮件、进程、GPU、IoT 或 agent 专有字段。
- Domain Profile 定义领域默认规则。
- Capability Document 定义 Provider 实际支持的领域和规则。
- Transport Binding 定义交付方式，不改变 Core 对象语义。
