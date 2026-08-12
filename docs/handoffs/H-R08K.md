# H-R08K Bundled Matrix 去重交接

- 状态：`NEEDS_AUTHORIZATION`
- 日期：2026-08-09
- 详细证据：`docs/verification/R-08K-bundled-matrix-deduplication.md`

## 已通过

- 旧 configured Matrix 插件已可恢复地移出发现树。
- bundled Matrix 插件目录保持存在。
- Manager 仅重启一次并恢复 running。
- duplicate plugin ID 警告已消失。

## 未通过

- channel online 未获得正向布尔证据。
- sync-ready 未获得正向布尔证据。
- 不可进入单次 S01 preflight。

## 下一步

需新授权 R-08L：仅用官方命令启用 bundled Matrix plugin ID，且仅重启 Manager 一次，再复核四个脱敏布尔门。未经授权不得继续。
