# EAP Consumer Checklist

## Discover

- [ ] 调用 `eap.discover`。
- [ ] 检查 EAP version。
- [ ] 检查 signal、event、operator、delivery、privacy、limits。

## Contract

- [ ] Contract 使用 schema 校验。
- [ ] Scope 不超过授权范围。
- [ ] PrivacyPolicy 明确 forbidden fields。
- [ ] Delivery return_policy 明确 severity 动作。
- [ ] MemoryPolicy 明确是否允许保存信息。

## Wait / Receive

- [ ] Agent 使用 `eap.wait` 处理长时间任务。
- [ ] 不使用固定短间隔轮询替代 wait。
- [ ] Push 验证签名和 timestamp。
- [ ] Stream 处理 keepalive 和 reconnect。

## Event Handling

- [ ] 校验 Attention Event schema。
- [ ] 校验 contract_id 和 source。
- [ ] 按 severity 和 delivery action 处理。
- [ ] 执行 ack required。
- [ ] 不保存 forbidden fields。

## Lifecycle

- [ ] 任务结束后 revoke。
- [ ] timeout 不视为失败。
- [ ] provider_error 使用退避。
