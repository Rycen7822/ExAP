# 13. Conformance and Package Checks

## 1. 等级定义

ExAP 使用分级验收，避免把包级 schema 自检外推为实现互操作证明。

| 等级 | 名称 | 验收范围 |
|---|---|---|
| C0 | Package self-check | 规范包自身可解析：JSON/YAML 文件、schema meta-validation、canonical `$ref`、manifest、版本、命名、防过时文本扫描。 |
| C1 | Schema and fixture validation | C0 加正例、负例、operator matrix、lifecycle method params、Attention Event type/status、profile、MCP/A2A 示例和 capability compatibility fixture。 |
| C2 | Provider API behavior | C1 加 provider test adapter，覆盖 discover、contract.create/get/list/update/pause/resume/revoke、wait、stream.open、attention.ack、status、observation.query。 |
| C3 | Rule evaluation transcript | C2 加 Observation/Event transcript，验证 Rule DSL、debounce、cooldown、hysteresis、correlation、semantic operator 与 expected Attention Event。 |
| C4 | Binding interoperability | C3 加 HTTP、SSE/Webhook、MCP、A2A、Local binding 的 wire compatibility、cancellation、cursor recovery、push/stream artifact schema 和错误响应。 |

`tests/conformance.py` 当前执行 C0 与 C1 包级检查。Provider 只有在通过 C2/C3 对应 adapter 后，才能声明支持相应实现等级。绑定互操作声明需要通过 C4。

## 2. C0/C1 包级检查

C0/C1 检查覆盖：

- Draft 2020-12 schema meta-validation。
- 版本化 canonical `$id` 与 `$ref` 解析。
- 示例 Contract、Attention Event、Capability Document、Lifecycle request 的 schema validation。
- Rule DSL operator matrix 的 targeted negative probes。
- Lifecycle method-specific params、duration、enum、ack snooze、JSON-RPC integer error envelope targeted probes。
- Attention Event CloudEvents `type` 与 `data.status` 绑定 probes。
- Capability compatibility 与 capability self-consistency probes。
- Profile schema、profile semantic check、parameter binding check。
- MCP tool input/output schema 与 A2A Agent Card structured binding check。
- YAML reference、manifest、命名迁移、防过时文本、schema property documentation、JSON parse。

## 3. C2 Provider API adapter

C2 adapter 必须以黑盒方式调用 Provider，并记录 request、response、state transition 和错误响应。最小操作表：

| Method | 行为要求 |
|---|---|
| `exap.discover` | 返回当前 Capability Document，包含 ExAP version、signals、event types、operators、delivery、bindings 和 profiles。 |
| `exap.contract.create` | 支持 `validate_only`、`idempotency_key`、capability rejection、privacy rejection 和 effective contract 返回。 |
| `exap.contract.get/list/update` | 支持状态读取、分页、乐观并发和更新后的完整校验。 |
| `exap.contract.pause/resume/revoke` | 产生明确 lifecycle state transition，并释放或恢复观察资源。 |
| `exap.wait` | 阻塞到 `return_reason`，支持 `timeout`、`cursor`、`include`、取消映射和并发 wait。 |
| `exap.stream.open` | 返回 stream metadata，并使用绑定定义的事件帧发送 Attention Event、summary、keepalive 和 error。 |
| `exap.attention.ack` | 支持 `seen`、`snooze`、`dismiss`、`escalate`，并执行 snooze duration 语义。 |
| `exap.status` | 返回压缩状态，带 `recent_events`、delivery 或 metrics 子集。 |
| `exap.observation.query` | 执行 authorization、privacy、retention、pagination 和 payload limits。 |

## 4. C3 Rule evaluation transcript

C3 fixture 由三部分组成：

1. Capability Document。
2. Attention Contract。
3. Ordered Observation/Event transcript。

Provider 运行 transcript 后必须输出 expected Attention Events、suppressed/internal event records、state transitions 和 delivery reports。Transcript 必须覆盖 signal、event、field filter、state、correlation、rate、relative change、semantic_match、debounce、cooldown 和 hysteresis。

## 5. C4 Binding interoperability

C4 fixture 按绑定定义 wire-level 行为：

- HTTP/OpenAPI：全部 endpoint、标准 Error schema、headers、pagination/cursor、idempotency key、SSE stream、auth requirements。
- MCP：Lifecycle tools、output schema、resources、progress、cancellation、logging 和 cursor recovery。
- A2A：Agent Card、Task、Message、Part、Artifact、streaming、push notification、natural-language validate-only draft flow。
- Local：stdio/socket framing、exit code、stderr/stdout 分离、backpressure 和 cancellation。

## 6. Certification Output

测试报告必须包含：

- 测试执行时间。
- 等级：C0、C1、C2、C3 或 C4。
- Schema 文件列表。
- Valid fixture、negative fixture、targeted probe 结果。
- Capability compatibility、profile instantiation、binding example 结果。
- Cross-reference、版本一致性、命名一致性结果。
- 失败项、修复说明和重跑命令。

本包包含 `tests/conformance.py` 与 `tests/conformance-report.md`，作为 C0/C1 package self-check 的当前可执行入口。
