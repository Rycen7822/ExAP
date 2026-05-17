# 11. Provider Development Guide

## 1. Provider 职责

Provider MUST 实现以下职责：

1. 发布 Capability Document。
2. 接收并校验 Attention Contract。
3. 解析 Scope 和 Subject。
4. 采集 Signal 和 Event。
5. 执行 Rule DSL。
6. 构建 Evidence 和 Attention Event。
7. 执行 PrivacyPolicy。
8. 通过 Delivery 交付事件。
9. 处理 Ack、Snooze、Revoke。
10. 记录 Audit log。

## 2. 组件结构

| 组件 | 职责 |
|---|---|
| Capability Service | 返回 Provider 能力。 |
| Contract Store | 存储 Contract、状态、版本。 |
| Subject Resolver | 解析 SubjectSelector。 |
| Collector | 采集 Signal 和 Event。 |
| Rule Engine | 评估 Condition。 |
| Window Store | 存储窗口样本和聚合状态。 |
| Evidence Builder | 根据 EvidencePolicy 构建证据。 |
| Privacy Filter | 执行最小化、脱敏、禁止字段检查。 |
| Delivery Engine | wait、push、stream、summary 交付。 |
| Audit Logger | 记录审计。 |

## 3. Contract 接收流程

Provider MUST 按顺序执行：

1. 解析 JSON。
2. Schema 校验。
3. EAP version 校验。
4. Consumer 认证。
5. Scope 授权。
6. SubjectSelector 解析。
7. Signal、Event、operator、aggregate capability 校验。
8. Rule 语义校验。
9. PrivacyPolicy 校验。
10. Delivery mode、transport、payload limit 校验。
11. Rule ID 唯一性校验。
12. 写入 Contract Store。
13. 返回 effective contract。

任一步失败时，Provider MUST 返回错误码，不得创建 active Contract。

## 4. Subject Resolver

Subject Resolver MUST 支持：

| Resolution | 行为 |
|---|---|
| `exact` | 按 `ref` 解析单一 Subject。 |
| `snapshot` | 创建时按 `match` 解析集合。 |
| `dynamic` | 运行期间持续匹配集合。 |

Resolver MUST 记录解析结果和权限决策，用于 audit。

## 5. Collector

Collector 采集 Observation 和 Event。Collector MUST 标记 source、observed_at、quality、privacy class 和 trace。采集失败 MUST 转换为 unknown 或 provider error，不得伪造正常值。

## 6. Rule Engine

Rule Engine MUST 支持三值逻辑：`true`、`false`、`unknown`。Rule Engine MUST 实现 debounce、cooldown、hysteresis 和 dedupe。Rule Engine MUST NOT 执行 Contract 中的任意代码。

## 7. Window 和聚合

Window Store MUST 使用事件时间或观测时间进行窗口计算。Provider MUST 在 capability 中说明最大窗口、采样间隔和聚合支持。窗口样本不足时，Rule 结果按 `missing` 处理。

## 8. Evidence Builder

Evidence Builder MUST 根据 Rule `evidence` 和 Contract `payload_limits` 选择证据。Evidence MUST 足以解释触发原因，但 MUST 遵守 PrivacyPolicy。

## 9. Delivery Engine

Delivery Engine MUST 根据 Rule `delivery_action` 或 Contract ReturnPolicy 决定动作。Blocking wait 必须只在匹配 `until` 条件时返回。Push 失败必须按 retry 策略处理。Stream 必须发送 keepalive。

## 10. Audit Logger

Audit Logger MUST 记录 Contract lifecycle、authorization decision、privacy decision、delivery attempt、ack action 和 provider error。Audit log MUST 受 retention 控制。

## 11. Provider 最低测试

Provider-Minimal MUST 通过：

- Schema 校验。
- Valid Contract 创建。
- Unknown signal 拒绝。
- Unknown operator 拒绝。
- Forbidden field 脱敏。
- Debounce 触发。
- Cooldown 抑制。
- Wait timeout。
- Revoke 停止观察。
- Ack required 处理。

## 12. 输出质量

Attention Event MUST 包含足够证据，使 Consumer 能判断事件为何触发。Provider MUST 控制 payload 大小，并用 summary 和 evidence 代替大段原始日志、邮件正文或文件内容。
