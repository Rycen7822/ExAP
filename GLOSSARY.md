# ExAP 术语表

| 术语 | 定义 |
|---|---|
| ExAP | External Awareness Protocol。用于环境感知契约、规则评估和注意力事件交付的通用协议。 |
| Consumer | 需要被提醒或接收环境变化的一方。类型包括 agent、application、service、user interface、automation、human proxy。 |
| Provider | 观察环境、评估规则、交付事件的一方。类型包括 local daemon、connector、monitoring service、broker、IoT gateway、cloud service、agent runtime。 |
| Broker | 转发或聚合 ExAP 事件、Contract、Capability 的中间组件。Broker 不改变 Rule 语义。 |
| Environment | 感知发生的边界。每个 Environment 使用 ExAP URI 标识。 |
| Subject | 被观察对象。每个 Subject 使用 ExAP URI 标识。 |
| Signal | Subject 上的可观察状态、指标或属性。Signal 名称使用点分层命名。 |
| Observation | 某一时刻对 Signal 的一次观测。 |
| Event | 一次离散事件。Event 可来自日志、系统 API、SaaS webhook、消息队列或传感器。 |
| Attention Contract | Consumer 创建、Provider 执行的关注契约。 |
| Rule | Contract 中判断“何时值得注意”的结构化规则。 |
| Condition | Rule 中的布尔表达式节点。ExAP Condition 不执行任意代码。 |
| Attention Event | 规则触发后交付给 Consumer 的结构化事件。 |
| Evidence | Attention Event 中支持触发原因的证据项。 |
| Delivery Action | Provider 对触发事件执行的交付动作。 |
| Blocking Wait | Consumer 调用 wait 后，Provider 阻塞到事件、超时或终止状态再返回。 |
| Push | Provider 主动向 Consumer 指定 endpoint 发送事件。 |
| Stream | Consumer 与 Provider 维持流式连接，Provider 持续发送事件。 |
| Pull with State Compression | Consumer 主动拉取压缩状态，Provider 不返回原始观测流。 |
| Ack | Consumer 对事件执行确认、延迟、忽略或升级。 |
| Profile | 某类场景的默认 Rule、Delivery、Privacy 模板。 |
| Capability Document | Provider 对自身能力的机器可读声明。 |
| ExAP URI | `exap://authority/type/id` 格式的标识符。 |
| Privacy Policy | Contract 中的用途、最小化、脱敏、保留和审计策略。 |
| Privacy Report | Attention Event 中说明实际包含与脱敏字段的报告。 |
| MCP Binding | 将 ExAP Lifecycle API 暴露为 MCP tools/resources/prompts 的 agent-to-tool 绑定。 |
| A2A Binding | 将 ExAP Provider 表示为 A2A agent，并以 task、message、part、artifact 传递 ExAP 对象的 agent-to-agent 绑定。 |
