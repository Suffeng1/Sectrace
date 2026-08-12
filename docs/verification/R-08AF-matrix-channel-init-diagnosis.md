# R-08AF Matrix Channel 初始化类别诊断

日期：2026-08-09

结论：`ROOT_CAUSE_CONFIRMED`

## 安全边界

- 仅执行有界、非 probe 的公开 OpenClaw health/channel/plugin/config 状态投影。
- 状态正文只在进程内按错误类别计数；未读取或输出凭据、token、账户、房间、用户、事件标识、配置正文、路径、原始日志或 stderr。
- 未写配置，未 enable/disable，未停止或重启 Manager，未发送 S01，未审批、apply/delete 或修改任何项目/运行时资源。

## 分类结果

失败类别：`configuration_not_enabled_or_invalid`

更精确的边界是：配置开关已启用，但公开配置校验未通过。

| 检查项 | 结果 |
|---|---:|
| Manager running | true |
| all public probes completed | true |
| plugin enabled | true |
| channel config present | true |
| channel enabled | true |
| combined config-enabled gate | false |
| channel online | false |
| sync-loop positive evidence | false |
| credential/auth error count | 0 |
| pairing error count | 0 |
| network error count | 0 |
| room subscription error count | 0 |
| sync error count | 0 |
| configuration error count | 4 |
| other public error count | 2 |
| diagnostic window | 4.5 seconds |

## 证据与反证

- plugin、channel 配置存在性和 channel enabled 均为 true，排除“单纯未启用”作为当前第一失败层。
- 公开配置校验产生 4 个配置错误；channel-online 与 sync-loop 均无正向证据。因此第一失败层是 Matrix/OpenClaw 配置 schema 或初始化配置无效。
- 认证、配对、网络、房间订阅和 sync 错误计数均为 0，但配置校验先失败意味着这些下游阶段可能尚未执行；不能据此宣称下游健康。
- 2 个其它公开错误属于配置失败后的伴随信号，当前没有证据将其提升为独立第一根因。

## 资格判定

当前不具备单次 S01 preflight 资格。

## 唯一最小修复授权建议

建议 R-08AG 仅授权一次结构化 schema 修复事务：

1. 通过公开 validator 在进程内只投影 Matrix 相关无效 schema 键的类别与计数，不输出键值或路径；
2. 必须断言恰好一个已废弃 Matrix schema 组/键类别；若不是 1，立即停止；
3. 仅删除或按当前 bundled Matrix schema 迁移该精确无效键，不读取或更改凭据及其它 channel 值；
4. 验证配置有效且其它配置语义不变；
5. 仅重启 Manager 一次，再复核 old-path-not-reproduced、bundled-only、duplicate-warning-absent、channel-online、sync-ready 五布尔。

不得使用无范围约束的 doctor 自动修复，也不得发送 S01。
