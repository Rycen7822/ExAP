# 15. Operations

## 1. 运行目标

ExAP Provider 的运行目标：低误报、低漏报、低延迟、低 token/带宽消耗、可审计、可恢复、可观测、可容量治理。

## 2. Health、readiness 与 metrics endpoint

HTTP binding Provider 暴露以下 endpoint；其他绑定提供等价机制：

| Endpoint | 定义 |
|---|---|
| `/healthz` | 进程存活检查。依赖不可用时仍可返回 alive，但必须报告 degraded reason。 |
| `/readyz` | 创建新 Contract、执行 wait/stream/push 的 readiness。Contract store、capability registry、delivery queue、collector freshness 任一关键依赖失效时返回 not ready。 |
| `/metrics` | Prometheus/OpenTelemetry 可抓取指标。 |

Readiness 必须包含 collector freshness、queue depth、contract store connectivity、clock drift、schema registry version 和 delivery worker 状态。

## 3. OpenTelemetry metrics

Provider 必须暴露以下指标，名称作为 OpenTelemetry semantic conventions 的初始集合：

| Metric | 类型 | 定义 |
|---|---|---|
| `exap.contract.active.count` | gauge | 活跃 Contract 数。 |
| `exap.contract.create.latency` | histogram | Contract 创建和校验耗时。 |
| `exap.rule.evaluation.latency` | histogram | Rule evaluation 耗时。 |
| `exap.rule.evaluations.count` | counter | Rule evaluation 次数。 |
| `exap.attention.events.delivered.count` | counter | 已交付 Attention Event 数。 |
| `exap.attention.events.suppressed.count` | counter | 已抑制 Attention Event 数。 |
| `exap.wait.active.count` | gauge | 活跃 wait 数。 |
| `exap.wait.duration` | histogram | wait 请求持续时间。 |
| `exap.delivery.queue.depth` | gauge | 待交付队列深度。 |
| `exap.delivery.dlq.count` | counter/gauge | DLQ 写入数与当前积压数。 |
| `exap.delivery.retry.count` | counter | delivery retry 次数。 |
| `exap.collector.freshness.seconds` | gauge | 最近 Observation/Event 到当前时间的秒数。 |
| `exap.privacy.redactions.count` | counter | 脱敏处理次数。 |

指标维度使用低基数字段：`provider_id`、`binding`、`delivery_mode`、`status`、`return_reason`、`error_exap_code`、`severity`。高基数字段如 `contract_id` 和 `subject_ref` 进入 trace/log，不进入默认 metric label。

## 4. Logs and traces

Provider logs 必须包含 `request_id`、`trace_id`、`contract_id`、`operation`、`decision`、`jsonrpc_code`、`exap_code`、`return_reason`。日志内容执行 Contract privacy policy 与 forbidden field redaction。

Trace span 命名：

| Span | 定义 |
|---|---|
| `exap.lifecycle.request` | Lifecycle method 收到、校验、调度。 |
| `exap.contract.validate` | Schema、capability、privacy、authorization、rule semantic validation。 |
| `exap.rule.evaluate` | 单次 Rule evaluation。 |
| `exap.wait.block` | wait 阻塞周期。 |
| `exap.delivery.send` | push/stream/webhook/MCP/A2A artifact 交付。 |
| `exap.dlq.write` | Dead letter 写入。 |

## 5. Backup、restore、RPO/RTO

Provider 必须备份 Contract Store、Capability snapshot、Rule state、dedupe/cooldown/hysteresis state、Delivery queue、DLQ 和 Audit Log。

| 项目 | 最低验收口径 |
|---|---|
| RPO | 生产 Provider 定义可接受数据丢失窗口，并在 capability 或 operations profile 中公布。 |
| RTO | 生产 Provider 定义恢复时间目标，并在演练报告中记录。 |
| Restore test | 每个发布周期至少执行一次恢复演练，验证 active Contract、wait cursor、delivery queue 和 audit log 可恢复。 |
| Failed recovery | 无法恢复的 Contract 标记为 `failed`，并产生 `exap.contract.state_changed`。 |

## 6. Rate limiting 与 storm control

Provider 必须对 Consumer、Contract、Subject、Rule、delivery endpoint 和 binding 维度执行限流。Rate limit 命中使用 JSON-RPC integer error code 与 `data.exap_code=ExAP-4290`。

Storm control 至少覆盖：dedupe、cooldown、summary aggregation、severity escalation gate、retry backoff、delivery endpoint circuit breaker。Retry backoff 使用指数退避与 jitter，并记录 retry storm 指标。

## 7. Dead Letter Queue

Push、webhook、stream artifact、MCP/A2A artifact 交付失败且 retry 用尽时，Provider 将记录写入 DLQ。

DLQ item schema 字段：

| 字段 | 定义 |
|---|---|
| `dlq_id` | DLQ item ID。 |
| `attention_id` | 关联 Attention Event。 |
| `contract_id` | 关联 Contract。 |
| `delivery_mode` | delivery mode。 |
| `transport` | transport kind。 |
| `attempts` | 已尝试次数。 |
| `last_error` | JSON-RPC code、ExAP code 或绑定错误。 |
| `next_retry_at` | 下次手动或自动重试时间。 |
| `created_at` / `updated_at` | 时间戳。 |

Provider 暴露 DLQ 查询 API 或运维等价机制，并支持按 `contract_id`、`attention_id`、`transport`、时间窗口过滤。

## 8. Time handling

Provider 使用单调时钟计算 duration、debounce、cooldown、timeout。事件时间、审计时间和展示时间使用 RFC 3339 date-time。分布式 Provider 记录 clock drift 指标，并在 drift 超出阈值时将 readiness 降级。

## 9. Multi-tenant isolation

多租户 Provider 必须隔离 Contract Store、Observation、Event、Audit、secret reference、capability view、DLQ 和 metrics export。跨租户 Subject 引用由 authorization validator 拒绝，并返回 `ExAP-4030` 或 `ExAP-4031`。

## 10. Incident runbook

Provider 事故记录包含：影响的 `contract_id`、`attention_id`、`subject_ref`、fields、时间范围、delivery endpoints、exap_code、处置动作、恢复时间、后续 preventive action。Runbook 至少覆盖：collector stale、wait starvation、delivery queue backlog、DLQ growth、retry storm、schema registry mismatch、authorization outage。

## 11. Deprecation

字段、operator、profile 或 binding 废弃时，Provider 在 capability 中标记 deprecated，并提供 removal version。废弃期内仍支持的字段保持原语义，并在 C2/C3/C4 fixture 中保留兼容测试。
