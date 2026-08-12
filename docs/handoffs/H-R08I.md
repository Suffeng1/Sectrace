# H-R08I Manager Matrix Plugin 去重交接

- 状态：`NEEDS_AUTHORIZATION`
- 日期：2026-08-09
- 前置验证：R-08H
- 详细证据：`docs/verification/R-08I-matrix-plugin-deduplication.md`

## 已完成

- 通过 OpenClaw 官方 dry-run 确认只移除 Matrix plugin config entry 并保留文件。
- 实际移除 config entry 成功。
- 仅滚动重启 Manager 一次，Manager 恢复 running。

## 未通过

- 重启后 duplicate Matrix plugin ID 警告再次出现。
- channel online 与 sync-ready 没有可安全投影的布尔接口，本轮未读取完整 channel/account/session JSON。
- Manager consumption 仍未证明恢复。

## 确认的新事实

直接编辑 Manager 当前 config entry 不具持久性；启动期存在上游配置来源重新注入 configured Matrix override。未经新授权不得读取该来源、再次修改或重启。

## 下一步

请求 R-08J 授权：只读确认重新注入的来源类别；确认后再授权在唯一源头移除 override、仅重启 Manager，并复核三个脱敏布尔值。

在三个布尔值全部通过前：

- 不进入单次 S01 preflight；
- 不发送或重试 S01；
- 不审批；
- 不修改 Worker/YAML/业务代码/MCP；
- 不触碰 smoke；
- 不 commit/push。
