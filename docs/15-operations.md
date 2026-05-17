# 15. Operations

## 1. 运行目标

EAP Provider 的运行目标：低误报、低漏报、低延迟、低 token/带宽消耗、可审计、可恢复。

## 2. Metrics

Provider MUST 暴露以下 metrics：

| Metric | 定义 |
|---|---|
| `eap.contract.active` | 活跃 Contract 数。 |
| `eap.rule.evaluations` | Rule 评估次数。 |
| `eap.attention.triggered` | 触发事件数。 |
| `eap.attention.suppressed` | 抑制事件数。 |
| `eap.delivery.attempts` | 交付尝试次数。 |
| `eap.delivery.failures` | 交付失败次数。 |
| `eap.wait.active` | 活跃 wait 数。 |
| `eap.privacy.redactions` | 脱敏次数。 |

## 3. Logs

Provider logs MUST 包含 request_id、contract_id、operation、decision、error_code。Logs MUST NOT 包含 secret、forbidden fields 或 raw sensitive payload。

## 4. Backup and Recovery

Provider MUST 备份 Contract Store 和 Audit Log。恢复后，Provider MUST 重新加载 active Contract，并根据 lifecycle、retention、dedupe、cooldown 状态恢复执行。无法恢复的 Contract MUST 标记为 `failed` 并产生 state changed event。

## 5. Rate Limiting

Provider MUST 对 Consumer、Contract、Subject 和 webhook endpoint 维度执行限流。Rate limit 命中返回 `EAP-4290`。

## 6. Event Storm Control

Provider MUST 实现至少两种事件风暴控制：dedupe、cooldown、rate limit、summary aggregation、severity escalation gate。

## 7. Dead Letter

Push 交付失败且 retry 用尽时，Provider MUST 将事件写入 dead letter store 或 audit log，并暴露查询方式。

## 8. Time Handling

Provider MUST 使用单调时钟计算 duration、debounce、cooldown、timeout。事件时间和展示时间使用 RFC 3339 date-time。

## 9. Multi-Tenant

多租户 Provider MUST 隔离 Contract Store、Observation、Event、Audit、secret reference 和 capability。跨租户 Subject 引用 MUST 被拒绝。

## 10. Incident Handling

Provider 发生隐私或安全事故时 MUST 记录影响的 contract_id、attention_id、subject_ref、fields、时间范围和处理动作。

## 11. Deprecation

字段、operator、profile 或 binding 废弃时，Provider MUST 在 capability 中标记 deprecated，并提供 removal version。废弃期内仍支持的字段 MUST 保持原语义。
