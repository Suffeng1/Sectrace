# R-08Q Supervisor Quiesced Repair 验证

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：双进程暂停状态断言
- 安全边界：失败立即停止；未读取或修改配置、未执行 enable、未重启 Manager、未发送 S01 或审批，未 apply/delete，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 暂停尝试

按授权顺序：

1. 精确定位 Manager 的对象存储出站 watcher；
2. 向 watcher 发送 pause；
3. 向 Manager PID 1 supervisor 发送 pause；
4. 只读检查两个进程是否同时处于 stopped 状态。

结果：

- 两个 pause 系统调用均未报告命令失败；
- “supervisor 与 watcher 同时处于 stopped”联合断言为 false；
- 本轮没有把不满足联合门的状态冒充为成功，也没有重试以区分单个失败项。

## 失败停止与恢复

联合断言失败后立即：

- 向 PID 1 supervisor 发送恢复信号；
- 向同一 watcher 发送恢复信号；
- 停止 R-08Q 后续步骤。

只读恢复确认：

- Manager 容器 running：true
- supervisor resumed：true
- watcher 存在：true
- watcher resumed：true

## 未执行事项

- effective JSON 断言/删除：未执行
- `plugins enable matrix`：0 次
- config validate：未执行
- Manager restart：0 次
- 四布尔验收：未执行
- S01/审批：未执行

因此没有配置或运行时半成品需要回滚。

## 当前结论

R-08P 的来源结论保持不变：旧路径唯一存在于 effective JSON。R-08Q 只证明当前组合式暂停方法无法可靠建立“双进程同时静止”的前置门；它没有验证或否定后续修复方案。

## 下一项唯一最小授权建议

建议 R-08R 仅做暂停机制校准，不修改配置：

1. 单独暂停 watcher，并在暂停 supervisor 前立即验证 watcher 状态；
2. 再单独暂停 PID 1 supervisor，改用 Docker host 侧进程状态投影验证 PID 1，避免依赖已暂停 supervisor 下的容器内检查；
3. 只输出两个独立 stopped 布尔；
4. 无论结果如何都恢复两个进程；
5. 不删除配置、不 enable、不重启。

只有 R-08R 证明两个独立暂停门都可靠，才重新申请结构化修复授权。也可由用户选择维护窗口直接停止 Manager，并由操作员离线修改模板，但这需要不同授权。

## 结论

`INCOMPLETE`

当前不可进入 S01 preflight。
