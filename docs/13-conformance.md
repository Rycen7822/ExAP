# 13. Conformance

## 1. 一致性等级

| 等级 | 定义 |
|---|---|
| Provider-Minimal | 支持 discover、contract.create、wait、attention.ack、contract.revoke、schema 校验和至少一种 delivery mode。 |
| Provider-Core | 支持全部 Lifecycle API、Rule DSL 基础条件、debounce、cooldown、hysteresis、privacy report。 |
| Provider-Advanced | 支持 correlation、semantic_match、多 transport、broker 或 durable stream。 |
| Consumer-Minimal | 支持 discover、contract.create、wait、event schema 校验、ack、revoke。 |
| Consumer-Agent | Consumer-Minimal 加 agent memory policy、blocking wait、payload trust boundary。 |

## 2. Provider-Minimal 要求

Provider-Minimal MUST：

- 通过所有 schema 校验测试。
- 返回 capability document。
- 拒绝 unsupported signal、event type、operator。
- 正确执行至少 `all`、`any`、`not`、`signal`、`event` 条件。
- 支持 `blocking_wait`。
- 执行 PrivacyPolicy。
- 生成 Attention Event。
- 支持 ack 和 revoke。

## 3. Consumer-Minimal 要求

Consumer-Minimal MUST：

- 读取 capability。
- 创建有效 Contract。
- 校验 Attention Event。
- 对 ack required 事件执行 ack。
- 在完成后 revoke。
- 对 timeout 执行非失败处理。

## 4. Schema Conformance

实现 MUST 使用本包 schemas 或语义等价的验证器。所有跨 schema `$ref` MUST 解析到 canonical `$id`。

## 5. 测试用例

| ID | 测试 | 期望 |
|---|---|---|
| `TC-001` | Valid process Contract | 通过。 |
| `TC-002` | Valid email Contract | 通过。 |
| `TC-003` | Valid Attention Event | 通过。 |
| `TC-004` | Capability document | 通过。 |
| `TC-005` | Profiles | 全部通过。 |
| `TC-006` | Unknown operator negative fixture | schema 或 semantic validation 失败。 |
| `TC-007` | Missing required field negative fixture | schema 失败。 |
| `TC-008` | Forbidden top-level field negative fixture | schema 失败。 |
| `TC-009` | Rule ID uniqueness | 重复时 semantic validation 失败。 |
| `TC-010` | Version consistency | 包内不含旧版本字符串。 |
| `TC-011` | Cross-schema reference resolution | 所有 `$ref` 可解析。 |
| `TC-012` | YAML references | OpenAPI 和 AsyncAPI 可解析为 YAML。 |

## 6. Certification Output

测试报告必须包含：

- 测试执行时间。
- Schema 文件列表。
- Valid fixture 结果。
- Negative fixture 结果。
- Cross-reference 结果。
- 版本一致性结果。
- 失败项和修复说明。

本包包含 `tests/conformance.py` 和 `tests/conformance-report.md`。
