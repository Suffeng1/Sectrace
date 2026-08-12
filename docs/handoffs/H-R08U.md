# H-R08U Root Helper 交接

- 状态：`INCOMPLETE`
- 日期：2026-08-09
- 详细证据：`docs/verification/R-08U-root-helper-maintenance-patch.md`

## 结果

一次性 root helper 按约束启动，但退出码为 1，未产生结构化摘要。helper 已通过 `--rm` 自动删除。

失败恢复：

- Manager 仅启动一次；
- Manager running；
- 无 helper、容器或卷残留。

## 下一步

需新授权 R-08V：不停止 Manager，只创建一次只读 helper 兼容性探针，使用 Manager 内确认的绝对 Node entrypoint，验证 Node/文件/JSON/count 四个门。

当前不可进入 S01 preflight。
