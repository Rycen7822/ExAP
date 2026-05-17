# 14. Reference Implementation

## 1. 参考实现目标

参考实现提供 ExAP Core 的可运行样例，不改变协议规范。参考实现名称固定为：`exapd`、`exapctl`、`exap-mcp-server`、`exap-a2a-agent`。

## 2. 组件结构

```text
reference/exapd/
  __init__.py
  common.py
  capability_service.py
  contract_store.py
  rule_engine.py
  evidence_builder.py
  delivery_engine.py
  fake_collectors.py
  audit_logger.py
  provider.py
reference/exapctl/
  __init__.py
  cli.py
reference/bindings/
  __init__.py
  http_server.py
  mcp_server.py
  a2a_agent.py
reference/smoke/
  run_reference_smoke.py
  expected/
    healthz.json
    readyz.json
    metrics.txt
  reports/
    reference-smoke-report.md
```

## 3. exapd 功能

`exapd` MUST 支持：

- capability endpoint。
- contract create/get/list/update/pause/resume/revoke。
- wait。
- stream。
- ack。
- status。
- observation query。
- process/file/log/GPU fake collector demo。
- delivery report 和 in-memory audit log。
- operations endpoint：`healthz`、`readyz`、`metrics`、DLQ query。

当前 smoke-grade adapter 为 `reference.exapd.provider:ReferenceProviderAdapter`，可直接作为 C2 provider behavior suite 的 target。

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

A2A Agent MUST 在 Agent Card 中声明 create contract、wait、ack 和 revoke skill。ExAP Attention Event MUST 作为 `application/exap+json` Artifact 返回。`text/plain` intent 返回 validate-only draft；active Contract 创建使用 structured JSON。

## 11. Smoke commands

```bash
python tests/provider_behavior/run_c2.py --adapter reference.exapd.provider:ReferenceProviderAdapter --report tests/provider_behavior/reports/c2-reference-report.md
python reference/smoke/run_reference_smoke.py --target all --report reference/smoke/reports/reference-smoke-report.md
```

当前 R4 smoke 覆盖：

- OpenAPI lifecycle endpoint presence 与 HTTP create/wait/status/ack/revoke smoke。
- MCP six-tool invocation 与 capability resource。
- A2A validate-only draft、structured create、wait、ack、revoke artifact。
- Operations `/healthz`、`/readyz`、`/metrics`、DLQ query。
