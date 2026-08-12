# H-R08L Bundled Matrix Enable 交接

- 状态：`NEEDS_AUTHORIZATION`
- 日期：2026-08-09
- 详细证据：`docs/verification/R-08L-bundled-matrix-enable.md`

## 结果

唯一授权命令 `openclaw plugins enable matrix` 在配置校验阶段失败。残留的旧 Matrix plugin load-path 指向已禁用目录，使 OpenClaw config invalid。

失败后立即停止：

- Manager 未重启；
- 未修改 channel 配置；
- 未运行 doctor；
- 未执行 S01、审批或其它资源操作。

## 下一步

需新授权 R-08M：只删除精确匹配旧 Matrix 插件路径的一个 load-path 条目，然后重新执行一次 enable、仅重启 Manager 一次并复核四项布尔门。

当前不可进入单次 S01 preflight。
