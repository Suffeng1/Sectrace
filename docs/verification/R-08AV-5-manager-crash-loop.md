# R-08AV-5 Post-Send Observation: Manager Crash Loop

日期：2026-08-10

结论：`SENT_OK_MANAGER_CRASH_LOOP`

## 范围

P5 之后的只读观察。S01 已由 WorkBuddy 浏览器自动化单次发送成功；观察 Manager 消费时发现 Manager 容器陷入崩溃循环，无法消费 S01。本票不做任何修改、不重启、不重发。

## 有界执行证据

- **S01 发送成功**：11:37 在 `Worker: sectrace-commander` 以 admin 身份 + 结构化 Manager mention 发送固定 S01（R-08AV-4 记录）。发送后输入框清空，房间最新消息确认 admin 的 S01 已上屏。
- **Manager 重启事件**：发送后观察期间，Manager 容器显示 `Up 47 seconds`（11:38 前后被 Controller 重建），其他 6 个容器 `Up 30 minutes`。
- **崩溃循环确认**：`docker inspect` 显示 Manager `restarts=62`，`Up 3 seconds` 后又退出——持续崩溃循环。
- **崩溃根因（只读确认）**：
  - `docker logs` 反复输出 `Config invalid`，错误为 `plugins.load.paths: plugin: plugin path not found: /opt/openclaw/extensions/matrix`。
  - 容器内 `ls /opt/openclaw/extensions/` 显示存在大量扩展（AGENTS.md、acpx、alibaba 等），但 **`matrix` 目录不存在**。
  - openclaw.json 中 `plugins.load.paths: ["/opt/openclaw/extensions/matrix"]` 指向不存在路径 → openclaw 启动校验失败 → 容器退出 → Controller 反复重启。
- **影响**：Manager 无法启动 → 无法消费 11:37 已发送的 S01 消息 → 链路停在 Manager 消费层。

## 结论判断

这是 **R-08AE 已修复过的"悬空插件引用"问题的配置回退复现**：Manager 容器被重建后，openclaw.json 重新生成，`plugins.load.paths` 又写入了 `/opt/openclaw/extensions/matrix`，而该路径在 v1.2.x 镜像中不存在（matrix 为 bundled 插件，不应出现在 load.paths）。

## 停止条件

未修改任何配置、未重启容器、未重发 S01、未审批、未触碰 `sectrace-smoke`、未 commit/push、未读取/输出秘密或 Matrix 标识。

## 下一授权建议

修复由 Codex 执行（WorkBuddy 只读协议）。最小修复方向：
1. 从 openclaw.json（容器内 `/root/manager-workspace/openclaw.json` 及 MinIO 权威副本）的 `plugins.load.paths` 移除 `/opt/openclaw/extensions/matrix`（保留 `plugins.entries.matrix.enabled=true`，matrix 为 bundled 插件）。
2. 确认启动权威模板/controller 生成 openclaw.json 的逻辑不会重新注入该路径。
3. 重启 Manager，确认崩溃循环停止、Matrix channel online。
4. 之后原路观察 11:37 已发送的 S01 是否被消费（消息已在 Matrix 服务器，Manager 恢复后 initial sync 应能拉到）。
