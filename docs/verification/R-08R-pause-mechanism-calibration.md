# R-08R Manager 暂停机制校准

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 安全边界：仅暂停/状态验证/恢复；未读取或修改 JSON 或其它配置，未 enable、restart、S01、审批、apply/delete，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 校准方法

1. 单独向 R-08N 已识别的精确对象存储出站 watcher 发送 pause。
2. 在暂停 PID 1 前，通过 watcher 自身进程状态验证。
3. 只有 watcher 门通过后，向 Manager PID 1 supervisor 发送 pause。
4. 不依赖容器内 supervisor 子进程，改用 Docker daemon 的 host-side `top` 状态投影验证 PID 1。
5. 使用无条件恢复路径向 supervisor 与 watcher 发送恢复信号。
6. 只读复核 Manager 与两个进程恢复状态。

## 两个独立布尔

| 门 | 结果 |
| --- | --- |
| watcher-stopped | true |
| supervisor-stopped | false |

补充：

- supervisor pause 命令本身没有返回错误；
- Docker host-side 投影成功找到精确容器 init 进程；
- 状态不是 stopped；
- `verification_anomaly=false`，因此该 false 不是查询缺失或解析异常。

## 无条件恢复

- Manager running：true
- supervisor resumed：true
- watcher resumed：true

没有遗留暂停进程。

## R-08Q 前提判断

不具备一次 R-08Q 修复的暂停前提。

原因：R-08Q 要求 supervisor 与 watcher 同时静止，但本轮证明当前容器内信号方法只能可靠暂停 watcher，不能可靠暂停 PID 1 supervisor。继续重复同一 STOP 方法不会增加证据。

## 下一项唯一最小授权建议

建议 R-08S 使用明确的 Manager 维护窗口，而不是进程级 STOP：

1. 仅停止 Manager 容器一次；
2. 通过 Docker 服务端字段投影在进程内取得 Manager workspace bind 源，不输出宿主路径；
3. 在容器停止期间，对 effective JSON 做结构化原子补丁：
   - 断言旧 load-path 恰好 1 次；
   - 只删除该数组项；
   - 仅把 bundled `matrix` plugin 的 enabled 布尔设为 true；
   - 验证其它配置值语义不变；
4. 仅启动 Manager 一次；
5. 复核旧路径是否在启动模板阶段复现，以及 bundled-only、duplicate-warning-absent、channel-online、sync-ready 四项布尔；
6. 任一失败立即停止，不发送 S01。

这需要新的明确授权，因为它将官方 enable 命令替换为容器停止期间的等价结构化布尔更新，并使用一次 stop/start 维护窗口。

## 结论

`INCOMPLETE`

当前不具备 R-08Q 修复前提，不能进入 S01 preflight。
