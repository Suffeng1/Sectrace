# H-R08AF Matrix Channel 初始化诊断交接

日期：2026-08-09

## 第一失败层

`configuration_not_enabled_or_invalid`，具体为配置已启用但 schema/初始化配置校验无效。

## 关键布尔与计数

- plugin enabled：true
- channel config present：true
- channel enabled：true
- public configuration errors：4
- channel online：false
- sync-loop positive：false
- auth/pairing/network/room/sync error counts：均为 0
- Manager running：true

下游错误计数为 0 不能视为下游健康，因为配置校验失败阻止了初始化链继续推进。

## 判定与唯一下一步

不可进入单次 S01 preflight。下一步仅建议 R-08AG：对公开 validator 识别的唯一已废弃 Matrix schema 组/键做结构化、值不透明的精确修复，配置有效后仅重启 Manager 一次并复核五布尔；不得运行无范围 doctor 或发送 S01。
