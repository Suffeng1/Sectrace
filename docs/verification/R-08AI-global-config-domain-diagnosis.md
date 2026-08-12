# R-08AI 全局配置域诊断

日期：2026-08-09

结论：`ROOT_CAUSE_CONFIRMED`

唯一问题三元组：`plugins_domain × unresolved_reference × 1`

## 安全边界

- 仅对 `config validate` 输出进行进程内域类别、无效项类别和匿名唯一指纹投影。
- 未输出键名、路径、值、配置正文、凭据、token、账户/房间/用户/事件标识、原始日志或 stderr。
- 未写配置，未运行 doctor、enable/disable，未停止或重启 Manager，未发送 S01，未审批、apply/delete 或修改任何资源。

## 初始投影与格式校准

首轮把 validator 总括失败行和具体问题行同时计入，得到 2 条和多个域/类别。该结果不能证明存在两个配置问题。

随后仅排除不含域/键结构的总括 envelope 行，对具体 issue record 重新生成匿名指纹；没有改变运行态或配置。

## 最终脱敏结果

| 检查项 | 结果 |
|---|---:|
| Manager running | true |
| validator completed | true |
| validator exit success | false |
| specific issue record count | 1 |
| top-level domain category | `plugins_domain` |
| invalid item category | `unresolved_reference` |
| unique invalid item count | 1 |
| unique problem confirmed | true |
| envelope lines excluded | true |

## 证据修正

- R-08AH 的全局配置校验门结论保持成立。
- R-08AG 的“没有 Matrix 专属无效 schema 键”结论保持成立。
- 当前唯一根因不是未知/废弃 schema 键，而是 plugins 域中的单个悬空引用。
- 由于 validator 在此处失败，channel-online 与 sync-ready 尚不能作为下游健康证据。

## 资格判定

当前不具备单次 S01 preflight 资格。

## 唯一最小修复建议

建议 R-08AJ 严格限定为：

1. 在 R-08AE 已确认的启动期权威结构化源中，以 validator 匿名身份定位这一个 plugins-domain unresolved reference；必须断言匹配恰好 1 且引用目标不可解析；
2. 仅删除该单个悬空引用，不删除插件实现、凭据、channel 值或其它插件配置；验证其它模板语义不变；
3. 不补触 effective config，不运行 doctor；
4. 仅重启 Manager 一次，先验证 config valid，再复核 old-path-not-reproduced、bundled-only、duplicate-warning-absent、channel-online、sync-ready 五布尔；
5. 任一门失败立即停止，不发送 S01。
