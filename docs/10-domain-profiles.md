# 10. Domain Profiles

## 1. 定义

Domain Profile 是特定场景的默认 Rule、Delivery、Privacy 和参数模板。Profile 不改变 EAP Core 语义。Profile JSON MUST 使用 `schemas/eap-profile.schema.json` 校验通过。

## 2. Profile 顶层字段

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `profile_id` | string | 是 | 格式 `profile:<name>`。 |
| `eap_version` | string | 是 | EAP 版本。 |
| `name` | string | 是 | 人类可读名称。 |
| `description` | string | 是 | Profile 说明。 |
| `domain` | string | 是 | 领域。 |
| `subject_types` | array[string] | 是 | 适用 Subject 类型。 |
| `signals` | array[string] | 否 | 常用 Signal。 |
| `event_types` | array[string] | 否 | 常用 Event type。 |
| `rules` | array[Rule] | 是 | 默认 Rule。 |
| `delivery` | object | 是 | 默认 delivery。 |
| `privacy` | PrivacyPolicy | 是 | 默认 privacy。 |
| `parameters` | array[object] | 否 | 可配置参数。 |
| `metadata` | object | 否 | 扩展元数据。 |

## 3. Profile Parameter

| 字段 | 类型 | 必填 | 定义 |
|---|---:|---:|---|
| `name` | string | 是 | 参数名。 |
| `type` | string | 是 | `string`、`number`、`integer`、`boolean`、`duration`、`datetime`、`array`、`object`。 |
| `required` | boolean | 是 | 是否必填。 |
| `default` | any | 否 | 默认值。 |
| `description` | string | 是 | 参数说明。 |

## 4. 包内 Profile

| 文件 | Profile ID | 场景 |
|---|---|---|
| `process-monitoring.eap.json` | `profile:process-monitoring` | 长时间进程和资源监控。 |
| `deep-learning-training.eap.json` | `profile:deep-learning-training` | 深度学习训练任务、GPU、日志、checkpoint。 |
| `email-priority.eap.json` | `profile:email-priority` | 重要邮件提醒。 |
| `calendar-focus.eap.json` | `profile:calendar-focus` | 重要日历事件提醒。 |
| `file-watch.eap.json` | `profile:file-watch` | 文件生成、修改和稳定性。 |
| `iot-safety.eap.json` | `profile:iot-safety` | IoT 传感器和安全事件。 |
| `ci-cd-monitor.eap.json` | `profile:ci-cd-monitor` | 构建、测试、部署流水线。 |

## 5. Profile 应用流程

1. Consumer 在 `eap.discover` 返回的 `profiles` 中选择 profile。
2. Consumer 将 profile rules 与用户或任务参数合成 Contract。
3. Provider 按 Contract 执行，而不是直接执行 profile 文件。
4. Provider MUST 对合成后的 Contract 执行完整 schema 和 capability 校验。

## 6. Profile 与 Contract 的关系

- Profile 是模板。
- Contract 是可执行对象。
- Profile 中的 Rule 可被复制到 Contract。
- Profile 中的参数替换 MUST 在 Contract 创建前完成。
- Profile 中未被 Provider capability 支持的 Rule MUST NOT 被创建为 active Contract。
