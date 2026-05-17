# EAP Provider Checklist

## Capability

- [ ] 发布 `eap.discover`。
- [ ] Capability document 通过 schema 校验。
- [ ] 声明 EAP versions、subject types、signals、event types、operators、aggregates、delivery modes、privacy capabilities、limits、bindings。

## Contract

- [ ] Contract 创建执行 schema 校验。
- [ ] Contract 创建执行 authorization 校验。
- [ ] Contract 创建执行 privacy 校验。
- [ ] Rule ID 唯一性被检查。
- [ ] Unsupported signal、event、operator、aggregate 被拒绝。

## Rule Engine

- [ ] 支持三值逻辑。
- [ ] 支持 debounce。
- [ ] 支持 cooldown。
- [ ] 支持 hysteresis。
- [ ] 支持 dedupe。
- [ ] Regex 有长度和时间限制。

## Delivery

- [ ] 支持至少一种 delivery mode。
- [ ] `eap.wait` 不使用短间隔返回状态替代阻塞等待。
- [ ] Push 有认证和 replay 防护。
- [ ] Stream 有 keepalive。
- [ ] Ack required 被执行。

## Privacy

- [ ] Forbidden fields 被删除或脱敏。
- [ ] PrivacyReport 被填充。
- [ ] Retention 被执行。
- [ ] Audit log 不含 secret。

## Tests

- [ ] `python tests/conformance.py` 通过。
