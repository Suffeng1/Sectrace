# R-08H Manager Consumption 只读运行态诊断

- 日期：2026-08-09
- 结论：`NEEDS_AUTHORIZATION`
- 范围：Docker Desktop 恢复与 Manager consumption 只读诊断
- 数据边界：未发送 S01，未审批，未读取或记录凭据、Matrix 标识、消息正文、原始日志或启动脚本

## 反馈环

本轮使用以下有界信号定位第一失败层：

1. Docker API、Controller、Manager、四个正式 Worker 与监听端口是否恢复；
2. 四个正式 Worker 的精确 `agt worker status`；
3. Manager 启动时公开的 OpenClaw Matrix plugin 装载警告；
4. 已安装的 configured override 与 bundled Matrix plugin 的非敏感版本、哈希差异和消费能力关键词计数。

所有命令均在 60 秒内结束。一次 Docker API 初始检查连续无输出后被终止，并在启动 Docker Desktop 后以 named-pipe 与 API 探针确认恢复。一次插件清单命令在 16.4 秒超时，未继续或重复；其公开输出已足以确认 Matrix plugin 覆盖关系。

## 当前运行态

- Docker Desktop 启动/恢复调用成功，Docker API 可达。
- Controller 容器：running；未配置 Docker healthcheck。
- Manager 容器：running；未配置 Docker healthcheck。
- 四个正式 Worker 精确查询均成功，全部为 Ready：
  - `sectrace-commander`
  - `sectrace-evidence`
  - `sectrace-response`
  - `sectrace-audit`
- 集群安全摘要：5 Workers、2 Teams。该总数包含既有非正式资源；本轮未查询、修改或清理它们。
- 正式 Team 的完整 JSON 查询会包含禁止读取的房间字段，因此安全放弃；未把历史 Active 状态冒充当前精确状态。
- 端口监听：18001、18080、18088、18888 为 true；19090 为 false。

## Manager Matrix channel 与消费链证据

### 已确认

- Manager 内 OpenClaw 版本为 2026.4.14。
- OpenClaw 每次公开 status/help 初始化都报告相同警告：Matrix plugin ID 重复，configured plugin 覆盖 bundled plugin。
- 实际加载的 configured Matrix plugin 版本为 2026.4.12，而 bundled/core 版本为 2026.4.14。
- configured override 与 bundled plugin 的入口哈希不同。
- 两份已安装的非敏感源码都含 sync、mention/requireMention、dedupe 和 sender/msgtype/self 类过滤能力标记；因此不能仅凭关键词缺失断言某个消费阶段不存在。

### 未确认

- 在不读取 Matrix 标识或 status 中最近会话 recipient 的前提下，无法安全取得当前 Matrix account 的在线布尔值。
- 禁止读取原始日志，因此不能把 R-08G 的单事件关联到 sync token 推进、ignored-event、dedupe、mention 或 sender/DM/msgtype 过滤分支。
- 未读取 Manager 配置值，当前 `requireMention=true` 与 `deepseek-chat` 只能作为 R-08C/R-08G 的历史已验证事实，不能冒充本轮实时复核。
- MCP 19090 当前未监听，但 R-08G 的第一失败层在 Manager consumption，尚无证据表明事件到达模型或 MCP；因此该端口不是当前已证实根因。

## 证据与反证

### 支持最高优先级假设的证据

- Manager 进程运行，Controller 与四个 Worker Ready，排除了“Docker 未恢复”作为当前解释。
- R-08G 已证明人类 admin/operator sender、正确入口 DM、正确 Manager mention 与 Matrix HTTP 200。
- Manager 当前用较旧的 configured Matrix plugin 覆盖与核心同版本的 bundled plugin，形成明确的运行时版本/职责错位。

### 反证与限制

- configured plugin 本身包含 sync、mention、dedupe 与过滤相关实现标记，不能证明它必然丢弃 R-08G。
- 没有事件级安全遥测或只返回类别的受支持接口，无法确认具体过滤门。
- 不能通过重发 S01、修改 requireMention、重启单资源或读取原始日志来补齐因果链；这些均不在本轮授权内。

## 根因排序

1. **Matrix plugin override 与 OpenClaw core 版本漂移或 handler 契约不兼容**：高优先级。直接证据是 2026.4.12 configured plugin 覆盖 2026.4.14 bundled plugin；尚未证实为单一根因。
2. **Manager Matrix sync/监听循环未推进或 channel 未实际在线**：中优先级。Manager 容器 running 不能证明 channel consumer 正在推进。
3. **事件被 sender/self/DM/msgtype/mention 过滤**：中低优先级。R-08G 已排除 sender 角色和 mention 目标错误，但仍可能存在 handler 级格式或 DM 过滤。
4. **dedupe/已读游标/session 去重误判**：低优先级。缺少与 R-08G 事件相关联的类别证据。
5. **Commander/MCP 后续失败**：当前低优先级；没有 Manager consumption 证据，且 19090 未监听发生在更后的层。

## 下一项精确授权

建议只授权一个最小变更阶段：

1. 备份但不输出 Manager 当前非敏感 plugin 选择元数据；
2. 移除或禁用仅导致重复 ID 的 configured Matrix plugin override，使 OpenClaw 2026.4.14 bundled Matrix plugin 成为唯一加载实现；
3. 仅滚动重启 Manager；
4. 不发送 S01，先用公开 channel status 取得不含 account/room/user 标识的 online、sync-ready 与 duplicate-warning 三个布尔值；
5. 由独立 QA 确认该最小变更与状态。

只有上述步骤通过后，才另行请求“唯一一次合成 S01”授权。不得把插件版本风险当作已修复根因，也不得在同一授权中顺带发送、审批、apply/delete Worker/Team、处理 smoke、commit 或 push。

## 结论

`NEEDS_AUTHORIZATION`

当前最强证据指向 Matrix plugin override 与 OpenClaw core 的版本/handler 契约漂移，但缺少事件级安全遥测，不能确认单一根因。下一步应先消除重复 plugin ID 并只重启 Manager，再验证 channel/sync 布尔状态；新的 S01 必须单独授权。
