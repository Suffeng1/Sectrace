# R-08AV-6 Manager Crash-Loop Root Cause Fix

日期：2026-08-10

结论：`FIXED_AND_VERIFIED`

## 背景

R-08AV-5 记录 Manager 容器陷入崩溃循环（restarts=62）：openclaw.json 的 `plugins.load.paths` 含 `/opt/openclaw/extensions/matrix`，但该路径在镜像中不存在 → `Config invalid` → openclaw 拒绝启动 → Controller 反复重建。

## 根因链（三层确认）

1. **Controller 生成源头**：`agentteams-controller/internal/agentconfig/generator.go:158` 硬编码 `"paths": []string{"/opt/openclaw/extensions/matrix"}`。Manager/Worker 的 openclaw.json 由 Controller 每次 reconcile（`reconcileInterval=5min`）重新生成并覆盖写入 MinIO + 本地挂载。
2. **union 合并无法清除**：`internal/service/deployer.go:1416-1437` `mergeUserPluginConfig` 对 `plugins.load.paths` 做 **union 合并**（generated ∪ existing）。即使清空 MinIO 副本，generated 侧恒定含该路径 → union 结果必含 → 无法通过只改数据根治。
3. **镜像路径事实**：openclaw 2026.4.x 的 bundled matrix 插件实际位于 `/opt/openclaw/dist-runtime/extensions/matrix`（有 index.js / package.json 等）；`/opt/openclaw/extensions/matrix` 是 legacy 路径，镜像中不存在。`openclaw doctor` 明确提示 "current packaged path is /opt/openclaw/dist-runtime/extensions/matrix"。

即：**legacy 路径引用 + Controller 每 5 分钟用 legacy 路径重新生成配置 + union 合并无法剔除** = 崩溃循环引擎。上游 `origin/main`（45eb463）同样未修复（grep 确认仍含该路径）。

## 修复内容（用户授权，2026-08-10 11:41）

### 1. 运行时立即止血（已生效）
- 容器内创建 symlink：`/opt/openclaw/extensions/matrix -> /opt/openclaw/dist-runtime/extensions/matrix`（legacy 路径可解析 → Config invalid 消失）。
- 验证：`openclaw doctor` 输出 `Matrix: ok (2ms)`、`Errors: 0`；openclaw-gateway 进程持续运行 3 分 33 秒无重启。

### 2. 持久化（容器重建后仍生效）
- 容器内启动脚本 `/opt/agentteams/scripts/init/start-manager-agent.sh` 注入 symlink 创建逻辑（openclaw 启动前 `mkdir -p /opt/openclaw/extensions && ln -sfn /opt/openclaw/dist-runtime/extensions/matrix /opt/openclaw/extensions/matrix`）。
- `docker commit agentteams-manager` → 新镜像 `agentteams-manager:legacy-path-fixed`（sha256:2a772869...），并 tag 覆盖 Controller 使用的正式镜像名 `higress-registry.cn-hangzhou.cr.aliyuncs.com/agentteams/agentteams-manager:latest`。

### 3. 源码根因修复（hiclaw 仓库，防未来重建镜像回退）
- `agentteams-controller/internal/agentconfig/generator.go:158`：`/opt/openclaw/extensions/matrix` → `/opt/openclaw/dist-runtime/extensions/matrix`。
- `manager/configs/manager-openclaw.json.tmpl:134`：同上。
- `manager/agent/skills/worker-management/references/worker-openclaw.json.tmpl:122`：同上。
- `manager/scripts/init/start-manager-agent.sh`：注入 symlink 兼容逻辑（与容器内一致）。

### 4. 数据副本
- 宿主机 `<local-manager-config>/openclaw.json`：`plugins.load.paths` 已写为 `["/opt/openclaw/dist-runtime/extensions/matrix"]`（备份 `openclaw.json.bak-20260810`）。
- MinIO `agentteams/agentteams-storage/agents/manager/openclaw.json`：已推送同步（注意：Controller 5 分钟 reconcile 可能重新写回 legacy 路径，但 symlink 兜底使其无害）。

## 验证结果

- `docker restart agentteams-manager` 后：`restarts=0`、`State.Status=running`。
- 日志确认：`[gateway] ready (7 plugins: acpx, browser, device-pair, matrix, memory-core, phone-control, talk-voice; 3.6s)`。
- matrix 插件从正确路径加载：`/opt/openclaw/dist-runtime/extensions/matrix/index.js`。
- Matrix channel 启动：provider 连接成功，DM/group allowlist 解析成功，已 join 房间。

## S01 链路恢复状态

- Manager 恢复后已消费 11:37 发送的 S01：Element 房间可见 Manager 回复「11:57收到，commander。已确认 commander 阶段完成（IncidentCase 已建，tr_s01 保留，severity=high，交接 evidence 正常）。请继续驱动 response→audit...」。
- 链路复用 task-20260809-101800（同 trace_id=tr_s01，state.json 中仍 active）。
- 当前阶段：**等待 sectrace-response 产出处置计划**（plan_ref=rp_tr_s01, requires_approval=true, status=pending_approval）。
- 已知观察：response worker 03:56 曾报 `unknown trace_id`（MCP 为 11:22 启动的新进程，内存态 trace 需 Commander 重建；Commander 已重建 IncidentCase）。

## 停止条件

未重发 S01、未审批、未触碰 `sectrace-smoke`、未 commit/push。源码修改未提交 git（保留为工作树改动，供 Codex 审查后提交）。

## 下一步

1. 继续只读观察 response worker 产出 rp_tr_s01 → pending_approval。
2. 出现审批门后由用户本人决定批准/拒绝。
3. 建议 Codex 审查 hiclaw 源码改动并决定是否 commit + 重建镜像（改动在 hiclaw 工作树）。
