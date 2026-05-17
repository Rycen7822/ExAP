# EAP：Environment Awareness Protocol

版本：`0.2.0-draft`  
日期：`2026-05-16`  
状态：社区草案

EAP 是用于声明、评估和传递环境感知契约的通用协议。EAP 让 Consumer 以结构化方式声明它关心的环境对象、信号、事件、触发条件、交付策略、证据范围和隐私边界；让 Provider 以能力文档声明自己能观察什么、能执行哪些规则、能通过哪些传输交付；让 Broker 或 Runtime 在条件满足时交付结构化、可验证、带证据、受权限约束的 Attention Event。

EAP 不限定于 coding agent。邮件、进程、GPU、文件、日历、IoT 设备、CI/CD、数据库、队列、网页、工单、pull request、云资源、人员状态和物理传感器都可作为 EAP Subject。EAP 的核心对象是 Attention Contract 和 Attention Event。

## 包内容

```text
README.md
VERSION.md
GLOSSARY.md
MANIFEST.md
CONTRIBUTING.md
docs/
  00-index.md ... 17-mcp-a2a-integration.md
schemas/
  eap-common.schema.json
  eap-rule.schema.json
  eap-attention-contract.schema.json
  eap-attention-event.schema.json
  eap-capability.schema.json
  eap-lifecycle-message.schema.json
  eap-observation.schema.json
  eap-profile.schema.json
profiles/
examples/
reference/
templates/
tests/
```

## 最小开发路径

1. Provider 实现 `eap.discover`，返回 capability document。
2. Consumer 读取 capability document，创建 Attention Contract。
3. Provider 使用 `schemas/eap-attention-contract.schema.json` 校验 Contract。
4. Provider 执行 Rule DSL，生成 Attention Event。
5. Provider 使用 `schemas/eap-attention-event.schema.json` 校验 Attention Event。
6. Consumer 使用 blocking wait、push 或 stream 接收事件。
7. Consumer 对需要确认的事件执行 `eap.attention.ack`，并在关注结束后执行 `eap.contract.revoke`。

## 核心定义

- **Environment**：感知发生的边界，例如个人工作区、项目、机器、家庭空间、企业租户、云环境。
- **Subject**：被观察对象，例如邮箱、进程、GPU、文件、目录、日历事件、传感器、队列、部署任务。
- **Signal**：Subject 上可观察的状态、指标或属性，例如 `process.cpu.percent`、`mail.message.received`、`file.modified_at`。
- **Observation**：一次原始观测记录。
- **Event**：一次离散事件记录。
- **Attention Contract**：Consumer 与 Provider 之间的关注契约，定义范围、规则、交付和隐私策略。
- **Attention Event**：规则触发后交付给 Consumer 的注意力事件，包含原因、证据、严重级别、交付动作和隐私报告。

## 设计边界

EAP 不替代 CloudEvents、AsyncAPI、OpenTelemetry、MQTT、NATS、Kafka、Webhook、OAuth、MCP 或 A2A。EAP 位于这些系统之上，定义“谁关心什么、何时提醒、携带什么证据、如何保护隐私”。EAP Attention Event 使用 CloudEvents 兼容 envelope。EAP Provider 可用 AsyncAPI 描述消息接口，可消费 OpenTelemetry signals，可通过 MCP 暴露工具，也可通过 A2A 表示为远程 agent 能力。

## 测试

执行：

```bash
python tests/conformance.py
```

测试覆盖 schema 语法、跨 schema 引用、示例、profiles、负面用例、YAML 参考文件、版本一致性和文档清单一致性。
