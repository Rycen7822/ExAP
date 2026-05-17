# ExAP Spec Package Manifest

## Root

| 文件 | 内容 |
|---|---|
| `README.md` | 英文默认概览和最小开发路径。 |
| `README.zh-CN.md` | 中文概览和最小开发路径。 |
| `VERSION.md` | 版本规则。 |
| `GLOSSARY.md` | 术语表。 |
| `CONTRIBUTING.md` | 贡献和变更规则。 |
| `MANIFEST.md` | 文件清单。 |

## Docs

| 文件 | 内容 |
|---|---|
| `docs/00-index.md` | 手册目录。 |
| `docs/01-overview-and-scope.md` | 目标、标准与绑定职责、角色、工作流。 |
| `docs/02-core-model.md` | 核心对象模型。 |
| `docs/03-attention-contract.md` | Attention Contract 字段定义。 |
| `docs/04-rule-dsl.md` | Rule DSL 字段和语义。 |
| `docs/05-attention-event.md` | Attention Event 字段定义。 |
| `docs/06-capability-discovery.md` | Capability Discovery。 |
| `docs/07-lifecycle-api.md` | Lifecycle API。 |
| `docs/08-transport-bindings.md` | Transport Bindings。 |
| `docs/09-privacy-security.md` | 隐私和安全。 |
| `docs/10-domain-profiles.md` | Domain Profiles。 |
| `docs/11-provider-development-guide.md` | Provider 开发手册。 |
| `docs/12-consumer-and-agent-guide.md` | Consumer 和 agent 对接手册。 |
| `docs/13-conformance.md` | 一致性测试。 |
| `docs/14-reference-implementation.md` | 参考实现结构。 |
| `docs/15-operations.md` | 运维要求。 |
| `docs/16-standards-compatibility.md` | 标准兼容性。 |
| `docs/17-mcp-a2a-integration.md` | MCP 和 A2A 集成。 |

## Schemas

| 文件 | 内容 |
|---|---|
| `schemas/exap-common.schema.json` | 公共类型。 |
| `schemas/exap-rule.schema.json` | Rule DSL。 |
| `schemas/exap-attention-contract.schema.json` | Attention Contract。 |
| `schemas/exap-attention-event.schema.json` | Attention Event。 |
| `schemas/exap-capability.schema.json` | Capability Document。 |
| `schemas/exap-lifecycle-message.schema.json` | Lifecycle API message。 |
| `schemas/exap-observation.schema.json` | Observation。 |
| `schemas/exap-profile.schema.json` | Domain Profile。 |

## Examples

| 文件 | 内容 |
|---|---|
| `examples/01-process-wait-contract.json` | 进程 wait Contract。 |
| `examples/02-gpu-idle-attention-event.json` | GPU idle Attention Event。 |
| `examples/03-email-important-contract.json` | 重要邮件 Contract。 |
| `examples/04-mail-attention-event.json` | 邮件 Attention Event。 |
| `examples/05-provider-capability-process.json` | 进程 Provider capability。 |
| `examples/06-provider-capability-mail.json` | 邮件 Provider capability。 |
| `examples/07-http-contract-create-request.json` | Contract create request。 |
| `examples/08-mcp-tools.json` | MCP tools 示例。 |
| `examples/09-a2a-agent-card.json` | A2A Agent Card 示例。 |
| `examples/10-local-cli.md` | Local CLI 示例。 |

## Profiles

| 文件 | 内容 |
|---|---|
| `profiles/process-monitoring.exap.json` | 进程监控。 |
| `profiles/deep-learning-training.exap.json` | 深度学习训练。 |
| `profiles/email-priority.exap.json` | 邮件优先级。 |
| `profiles/calendar-focus.exap.json` | 日历关注。 |
| `profiles/file-watch.exap.json` | 文件关注。 |
| `profiles/iot-safety.exap.json` | IoT 安全。 |
| `profiles/ci-cd-monitor.exap.json` | CI/CD 监控。 |

## Reference

| 文件 | 内容 |
|---|---|
| `reference/openapi-http-binding.yaml` | HTTP Binding OpenAPI 草案。 |
| `reference/asyncapi-provider.yaml` | Provider event stream AsyncAPI 草案。 |
| `reference/exapd/*.py` | Smoke-grade reference Provider：capability、contract store、rule compatibility、evidence、delivery、collector、audit、provider adapter。 |
| `reference/exapctl/cli.py` | Smoke-grade exapctl command facade。 |
| `reference/bindings/*.py` | HTTP、MCP、A2A reference binding facade。 |
| `reference/smoke/run_reference_smoke.py` | R4 reference smoke runner。 |
| `reference/smoke/expected/*` | R4 operations smoke expected outputs。 |
| `reference/smoke/reports/reference-smoke-report.md` | R4 reference smoke report。 |

## Tests

| 文件 | 内容 |
|---|---|
| `tests/conformance.py` | C0/C1 package self-check。 |
| `tests/conformance-report.md` | C0/C1 package self-check report。 |
| `tests/fixtures/negative/*.json` | 负面用例。 |
| `tests/fixtures/profile-instantiations/*.json` | Profile 实例化与 capability compatibility fixture。 |
| `tests/provider_behavior/` | C2 Provider behavior adapter、fake provider、cases、expected data 与 reports。 |
| `tests/fixtures/profile-transcripts/*/*.json` | C3 Profile transcript fixtures。 |
| `tests/profile_evaluation/` | C3 transcript schema、evaluator、runner 与 report。 |
| `tests/interoperability/` | C4 binding adapters、scenarios、transcript comparator、runner 与 report。 |
| `tests/audit-notes.md` | 历史修订审计记录，发布时作为 archive/internal 材料处理。 |
| `tests/draft-plan.md` | 修订计划记录。 |
