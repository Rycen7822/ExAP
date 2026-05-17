# 09. Privacy and Security

## 1. 定义

ExAP 可处理邮件、文件、进程、日志、日历、IoT、云资源和 agent 任务等高敏感环境信息。PrivacyPolicy、authorization、consent、retention、redaction 和 audit 是 Core 规范的一部分。

## 2. 安全原则

| 原则 | 强制行为 |
|---|---|
| 明确授权 | Provider MUST 在创建 Contract 前验证 Consumer 是否有权观察 scope。 |
| 数据最小化 | `privacy.data_minimization=true` 时，Provider MUST 只交付规则判断和下一步处理所需字段。 |
| 字段级控制 | Provider MUST 删除或脱敏 `forbidden_fields`。 |
| 可审计 | `privacy.audit.enabled=true` 时，Provider MUST 记录 Contract 创建、更新、撤销、交付和 ack。 |
| Secret 隔离 | Secret MUST NOT 出现在 Contract、Attention Event、Evidence、logs 或 audit payload 中。 |
| 透明保留 | Provider MUST 根据 retention 删除或冻结数据。 |

## 3. Scope 与授权

授权检查至少覆盖：

| 维度 | 示例 |
|---|---|
| Subject scope | 是否允许读取 `mailbox:primary` 或 `process:18423`。 |
| Signal scope | 是否允许读取邮件正文摘要或仅允许 metadata。 |
| Event scope | 是否允许读取日志行、文件路径、进程退出码。 |
| Payload scope | 是否允许交付 raw payload、summary 或 redacted excerpt。 |
| Action scope | 是否允许 ack、revoke、pause、resume、kill 或 archive。 |
| Retention scope | 是否允许保存 Observation、Event 和 audit logs。 |

## 4. Consent

Provider 涉及个人数据、通信内容、日历、位置或敏感文件时 MUST 要求 consent 或等价组织策略。`privacy.consent_ref` 指向 consent 记录。Consent 记录 MUST 可审计、可撤销。

## 5. Redaction

Redaction mode：

| Mode | 定义 |
|---|---|
| `none` | 不脱敏。仅在数据分类允许时使用。 |
| `mask` | 用掩码替换部分内容。 |
| `hash` | 用不可逆 hash 替换。 |
| `summary_only` | 只输出摘要，不输出 raw 内容。 |
| `drop` | 删除字段。 |

Provider MUST 在 PrivacyReport 中列出 `fields_redacted`。`redaction.include_redaction_report=true` 时，Provider MUST 填写 `redaction_report`。

## 6. Retention

Retention 使用 ISO 8601 duration。

| 字段 | 定义 |
|---|---|
| `observations` | 原始观测保留期。 |
| `events` | Attention Event 保留期。 |
| `audit_logs` | 审计日志保留期。 |

`PT0S` 表示不保留。Provider MUST 在保留期结束后删除数据或执行不可逆匿名化。

## 7. Audit

Audit log MUST 包含：

| 字段 | 定义 |
|---|---|
| `time` | 审计时间。 |
| `actor` | 操作主体。 |
| `operation` | 操作名。 |
| `contract_id` | Contract ID。 |
| `attention_id` | Attention ID，若适用。 |
| `decision` | allow、deny、redact、deliver、suppress。 |
| `reason` | 决策原因。 |
| `trace_id` | 追踪 ID。 |

Audit log MUST NOT 包含 forbidden fields 或 secret。


## 7.1 Audit Policy 字段

| 字段 | 类型 | 定义 |
|---|---:|---|
| `enabled` | boolean | 是否启用审计。 |
| `user_visible` | boolean | 审计记录是否可被最终用户查看。 |
| `log_fields` | array[string] | 允许写入审计日志的字段路径白名单。 |

## 8. Secret Handling

- `auth_ref` 引用凭据，不存储凭据值。
- Provider MUST 在日志和事件中扫描常见 secret 字段名：`token`、`password`、`secret`、`credential`、`api_key`、`Authorization`。
- Secret 泄漏检测命中时，Provider MUST 脱敏并记录 PrivacyReport。

## 9. Action Safety

ExAP Core 不自动执行 destructive action。Provider 支持动作时，动作 MUST 出现在 capability `actions` 中，并声明 action scope、确认要求和审计字段。

Agent Consumer MUST NOT 根据 Attention Event 自动执行 destructive action，除非 Contract、权限和用户/组织策略明确允许。

## 10. Threat Model

| 威胁 | 防护 |
|---|---|
| 越权观察 | Scope 授权和 capability 校验。 |
| 敏感数据外泄 | Forbidden fields、redaction、payload limits。 |
| 事件重放 | Event ID、timestamp、签名、dedupe。 |
| 事件风暴 | Cooldown、dedupe、rate limit。 |
| 恶意规则 | 禁止任意代码、限制 regex、限制 semantic provider。 |
| 提示注入 | Agent Consumer 必须把 payload 视为不可信输入。 |
| 工具滥用 | MCP tool 调用需要 host consent。 |
| 伪造 Provider | TLS、签名、认证、capability pinning。 |

## 11. Data Classification

Sensitivity 允许值：

| 值 | 定义 |
|---|---|
| `public` | 可公开数据。 |
| `internal` | 内部运营数据。 |
| `confidential` | 受限业务或个人数据。 |
| `secret` | 高敏感数据。 |
| `restricted` | 法规、合同或组织策略严格限制的数据。 |

Provider MUST 在 capability 或 Subject metadata 中声明默认 sensitivity。Contract PrivacyPolicy 可进一步限制。

## 12. Privacy by Default

Provider 默认行为：

- 未授权时拒绝 Contract。
- 未声明 allowed fields 时只返回最小 Evidence。
- 命中 forbidden fields 时删除或脱敏。
- 未声明 retention 时使用 Provider 最短默认保留期。
- 未知 Consumer capability 时不交付 raw payload。
