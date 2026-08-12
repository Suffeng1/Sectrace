# H-R08M Stale Load Path 交接

- 状态：`NEEDS_AUTHORIZATION`
- 日期：2026-08-09
- 详细证据：`docs/verification/R-08M-stale-load-path-removal.md`

## 已确认

- 旧 Matrix load-path 精确出现一次。
- 结构化删除成功：目标为 0、数组仅减少一项、其它配置值语义不变。
- 在未重启 Manager 的情况下，唯一 enable 命令仍看到相同旧路径。

## 结论

活动 Manager 配置协调器会重新注入旧 load-path。重复删除或 enable 不会形成持久修复。

## 停止状态

- enable 仅执行一次并失败；
- Manager 未重启；
- 未执行运行态四布尔探针；
- 不可进入 S01 preflight。

## 下一步

需新授权 R-08N，只读定位持续写入者类别；确认唯一协调器后再授权停写、精确修复和单次恢复。
