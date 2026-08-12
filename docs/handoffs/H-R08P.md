# H-R08P Effective Config Source 交接

- 状态：`ROOT_CAUSE_CONFIRMED`
- 日期：2026-08-09
- 详细证据：`docs/verification/R-08P-effective-config-source-diagnosis.md`

## 唯一来源层

effective JSON：

- 默认规范路径与 R-08M 编辑目标相同；
- 旧路径恰好 1 次；
- persisted plugin registry 不存在；
- CLI validate 只复现 JSON 中同一条。

## 已排除

- 编辑错文件；
- legacy/SQLite plugin registry；
- 独立 CLI derived registry view；
- 对象存储入站 watcher。

## 下一步

需新授权 R-08Q：暂停 Manager supervisor 与出站 watcher，在 supervisor 静止期间精确删除 JSON 条目、enable bundled Matrix，然后只重启 Manager 一次并复核四布尔。

当前不可进入 S01 preflight。
