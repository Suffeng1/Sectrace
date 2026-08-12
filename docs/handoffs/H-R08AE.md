# H-R08AE 启动期权威源修复交接

日期：2026-08-09

## 已完成

- 唯一权威源类别：`controlled_mount_json_template`。
- 旧路径计数在模板中从 1 精确变为 0。
- bundled Matrix `enabled=true`，其它模板语义不变。
- Manager 仅 restart 一次并恢复 running。
- restart 后 old-path 不复现、bundled-only、duplicate-warning-absent 均为 true。

## 剩余失败

- channel-online=false
- sync-ready=false

插件选择与启动模板问题已排除；剩余边界是 Matrix channel 初始化/同步层。

## 判定与唯一下一步

不可进入单次 S01 preflight。下一步仅建议 R-08AF 纯只读 channel 初始化类别诊断，不改配置、不 restart、不发送 S01。
