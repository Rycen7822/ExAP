# Contributing to ExAP

## 1. 变更类别

| 类别 | 影响 |
|---|---|
| Core schema change | 影响 Contract、Rule、Attention Event、Capability、Profile 或 Lifecycle message。 |
| Domain profile change | 影响某个领域模板，不改变 Core。 |
| Transport binding change | 影响 HTTP、Webhook、SSE、WebSocket、MQTT、NATS、Kafka、Local、MCP、A2A 映射。 |
| Documentation change | 只改变说明，不改变 schema 或 conformance。 |

## 2. 字段新增规则

- 新增 Core 字段 MUST 同步更新 schema、对应文档、示例和 conformance 测试。
- 新增可选字段 MUST 明确默认值和未知字段处理规则。
- 新增扩展字段 MUST 放入 `metadata` 或领域 profile；Core schema 不接受任意顶层字段。

## 3. Operator 新增规则

- 新增 operator MUST 在 `docs/04-rule-dsl.md`、`schemas/exap-rule.schema.json`、capability 示例和负面测试中同步更新。
- Operator MUST 具有确定性输入、输出和缺失值语义。
- Operator MUST NOT 执行任意用户代码。

## 4. Profile 新增规则

- 新 profile 文件 MUST 使用 `schemas/exap-profile.schema.json` 校验通过。
- Profile rule_id MUST 在 profile 内唯一。
- Profile MUST 定义 privacy policy。

## 5. 测试要求

修改者 MUST 执行：

```bash
python tests/conformance.py
```

测试通过后，`tests/conformance-report.md` MUST 被更新。
