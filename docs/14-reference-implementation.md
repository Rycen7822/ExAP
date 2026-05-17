# 14. Reference Implementation

## 1. 参考实现目标

参考实现提供 ExAP Core 的可运行样例，不改变协议规范。参考实现名称固定为：`exapd`、`exapctl`、`exap-mcp-server`、`exap-a2a-agent`。

## 2. 组件结构

```text
exapd/
  capability_service.py
  contract_store.py
  subject_resolver.py
  collectors/
  rule_engine.py
  evidence_builder.py
  privacy_filter.py
  delivery_engine.py
  audit_logger.py
exapctl/
  cli.py
bindings/
  http_server.py
  mcp_server.py
  a2a_agent.py
```

## 3. exapd 功能

`exapd` MUST 支持：

- capability endpoint。
- contract create/get/list/update/pause/resume/revoke。
- wait。
- stream。
- ack。
- status。
- process/file/log collector demo。
- privacy filter。
- audit log。

## 4. exapctl 命令

| 命令 | ExAP method |
|---|---|
| `exapctl discover` | `exap.discover` |
| `exapctl contract create` | `exap.contract.create` |
| `exapctl wait` | `exap.wait` |
| `exapctl status` | `exap.status` |
| `exapctl ack` | `exap.attention.ack` |
| `exapctl contract revoke` | `exap.contract.revoke` |

## 5. State Store

State store MUST 保存 Contract、Contract 状态、Rule 状态、dedupe keys、cooldown windows、pending ack、audit records。Observation 存储受 PrivacyPolicy 控制。

## 6. Collector

参考实现 collector：

| Collector | Subject | Signal / Event |
|---|---|---|
| Process | process | `process.status`、`process.cpu.percent`、`process.memory.rss_mb`、`process.exited`。 |
| File | file | `file.exists`、`file.size.bytes`、`file.modified_age.seconds`。 |
| Log | process/file | `log.line.appended`。 |
| GPU | gpu | `gpu.util.percent`、`gpu.memory.used_mb`。 |

## 7. Rule Engine 约束

Rule Engine MUST 实现三值逻辑、窗口聚合、debounce、cooldown、hysteresis、dedupe。Regex 执行 MUST 有超时和长度限制。

## 8. HTTP Server

HTTP Server MUST 实现 `08-transport-bindings.md` 中 HTTP endpoints。所有请求和响应 MUST 带 trace 或 request ID。

## 9. MCP Server

MCP Server MUST 暴露 `exap_discover`、`exap_contract_create`、`exap_wait`、`exap_status`、`exap_attention_ack`、`exap_contract_revoke` tools。输入 schema MUST 与 ExAP schemas 对齐。

## 10. A2A Agent

A2A Agent MUST 在 Agent Card 中声明 create contract 和 wait skill。ExAP Attention Event MUST 作为 `application/exap+json` Artifact 返回。
