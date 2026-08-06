# V-05-LIVE：生产 Worker mcporter 提示词滚动验证

日期：2026-08-05

## 授权范围

- 仅修改四个生产 Worker YAML 的 `spec.agents` 提示词。
- 不修改 MCP endpoint、MCP server、Team YAML、Worker 其它字段或 smoke 资源。
- 四个资源逐个 apply 并等待 Ready；全部 Ready 后仅重发一次合成 S01。
- 不记录凭据、Matrix 标识或原始运行时输出，不模拟人工审批或真实处置。

## TDD 与静态范围

- RED：新增资源测试后，旧提示词缺少强制 `mcporter` 调用规则，测试按预期失败。
- GREEN：四份 YAML 分别加入角色对应的 `mcporter call` 命令，并明确禁止直接 HTTP、curl、浏览器或 fetch MCP URL。
- 回归结果：资源、安全与 MCP 绑定相关测试共 8 passed。
- diff 校验：四份 Worker YAML 各仅新增一段 prompt；Team YAML 无差异；endpoint 与其它 Worker spec 未变。

## 滚动结果

按精确资源名顺序执行，四次 apply 均成功且每个 Worker 均达到 Ready：

1. `sectrace-commander`
2. `sectrace-evidence`
3. `sectrace-response`
4. `sectrace-audit`

滚动后 Team 为 Active，Leader Ready，三个成员 Worker Ready。

## 唯一一次 S01 与观察结果

- 前置路由拓扑满足；Manager 向 Commander Worker Room 定向提交一次原合成 S01，并显式 mention Commander。
- 发送命令成功并返回结构化回执；未重试。
- Commander 出现一个活动会话，但未观察到 shared task、Team 链路或 pending approval。
- Commander 脱敏日志聚合：`mcporter` 提及 0、已注册 sectrace 工具名提及 0、`/mcp` 路径提及 0；HTTP 404 特征 26、Matrix HTML 特征 52。未保存或输出原始日志。

## 结论

资源修改、测试、逐个滚动和 Ready 门均通过，但唯一一次 S01 仍返回原 404/Matrix HTML 失败特征。运行实例没有证据表明执行了 prompt 中要求的 `mcporter` 命令，因此 Commander→MCP→Team 链路与真实审批门仍未建立。

本轮按授权停止：不再次发送 S01，不修改配置，不重启资源，不触碰 smoke 或凭据。后续应定位运行时是否允许模型执行 `mcporter` CLI，或是否存在覆盖 Worker prompt/工具执行策略的更高层配置；在获得新授权前不做运行时变更。
