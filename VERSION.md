# ExAP 版本

当前版本：`0.2.0-draft`。

## 版本格式

ExAP 版本字符串使用：

```text
MAJOR.MINOR.PATCH[-PRERELEASE]
```

字段定义：

| 字段 | 定义 |
|---|---|
| `MAJOR` | 破坏性协议变更编号。 |
| `MINOR` | 向后兼容的功能新增编号。 |
| `PATCH` | 向后兼容的修复编号。 |
| `PRERELEASE` | 草案、预发布或测试标记。 |

## 兼容性规则

- Provider MUST 在 capability document 的 `exap_versions` 中列出支持的 ExAP 版本。
- Consumer MUST 在创建 Contract 前选择 Provider 支持的版本。
- Provider MUST 拒绝未知 MAJOR 版本。
- Provider MAY 接受相同 MAJOR 下较低 MINOR 的 Contract，前提是所有字段、operator、delivery mode 和 privacy policy 均被支持。
- Schema `$id` 在同一发布包内 MUST 保持唯一。
