# D-06 只读诊断：Worker 运行时工具策略

日期：2026-08-06

范围：只读审查 Worker 资源与 prompt、MCP 适配层、脱敏运行时证据和公开状态。未读取凭据、标识、原始日志或本地敏感配置；未重发 S01，未修改运行时或配置。

## 1. 证据

1. **失败边界已定位在 Commander → 工具执行。** Manager → Commander 路由已被观察到；Commander 返回 Matrix HTML 404，且尚未出现 Leader-to-Team delegation。见 `docs/verification/V-05-LIVE-commander-mcp-runtime.md:7-13`。
2. **传输与注册链路已有正证据。** 主机和 Commander 容器的 MCP initialize 均为 HTTP 200、JSON-RPC；运行时登记了一个 `sectrace` server；R-08B 的当前 allowlist 为六个工具。见 `docs/verification/V-05-LIVE-mcp-stage-b.md:5-22`、`docs/verification/V-05-LIVE-commander-mcp-runtime.md:14-28`。
3. **Worker prompt 已要求 mcporter，但这是文本约束。** 四个 Worker 资源要求使用已安装的 `mcporter` CLI，并禁止直接 HTTP/curl/browser/fetch；资源测试只断言 prompt 文本和资源字段。见 `hiclaw/sectrace-agents/sectrace-commander.yaml:9-22`、`tests/runtime/test_production_agent_resources.py:60-71`。
4. **仓库没有 Worker 运行时的工具调用代码门禁。** `src/app/mcp_adapter.py` 只负责 MCP server 侧 allowlist、trace 前置条件和安全 envelope；它不控制 OpenClaw 是否能启动 CLI，也不验证模型是否实际调用了工具。见 `src/app/mcp_adapter.py:28-58`、`138-161`。
5. **工具本身的本地链路是确定性的。** 六个工具按 intake → evidence → response → approval → audit 顺序工作，缺少前置阶段会拒绝；本地测试还验证未知/执行类工具被拒绝。见 `src/app/mcp_adapter.py:43-58`、`tests/integration/test_mcp_adapter.py:11-42`。
6. **脱敏日志聚合没有看到工具执行痕迹。** 有界 OpenClaw 日志元数据包含 404/HTML 标记，却没有 `mcporter`、SecTrace 工具名或 MCP 路径标记；日志正文未被记录。见 `docs/verification/V-05-LIVE-commander-mcp-runtime.md:30-38`。
7. **公开状态只证明会话存在，不证明工具调用或下游 handoff。** 修复后的单次合成 S01 观察到 Commander 有活动会话，但 Evidence/Response/Audit 没有活动会话，也没有 Manager shared-task、Leader-to-Team 或 pending approval 证据。见 `docs/verification/V-05-LIVE-s01-after-mcp-fix.md:13-21`。
8. **模型配置存在，但模型调用能力未被独立证明。** Worker 资源固定声明模型、运行时和 Running 状态；没有脱敏证据证明该模型 turn 获得了 shell/CLI 执行能力、收到了 `mcporter` 可执行说明，或成功消费工具结果。见 `hiclaw/sectrace-agents/sectrace-commander.yaml:5-18`。

## 2. 反证

- 当前问题不是单纯的 MCP listener 不可达：阶段 B 已证明协议握手从两个网络视角成功，且没有再次修改 Worker endpoint。见 `docs/verification/V-05-LIVE-mcp-stage-b.md:9-22`。
- 当前问题不是“CRD 字段完全被忽略”或“没有注册 server”：Commander 的运行时状态和 mcporter 列表均显示注册存在。见 `docs/verification/V-05-LIVE-commander-mcp-runtime.md:14-28`。
- OpenClaw 原生 MCP registry 为空不能单独作为故障证据；已安装 CRD 的约定是 Worker MCP 通过 mcporter 调用，而非进入原生 registry。见 `docs/verification/V-05-LIVE-commander-mcp-runtime.md:16-18`。
- 仅继续加 prompt 不是已证实的修复路径：四个 prompt 的 mcporter 规则已滚动验证，但单次合成 S01 后仍没有 Team 链或 pending approval。见 `docs/verification/V-05-LIVE-mcporter-rollout.md:14-17`、`32-41`。
- 本地 MCP 适配器和本地 replay 的正常结果不能证明远端 Worker turn 正常；二者绕过了 OpenClaw 的系统 prompt、工具注入和 CLI 执行层。见 `src/app/orchestrator.py:35-91`、`tests/integration/test_mcp_adapter.py:21-36`。

## 3. 根因假设排序

1. **高：运行时没有把“必须通过 mcporter 成功调用”做成执行门禁。** 模型可以选择普通 HTTP/浏览器路径，或者在工具失败后仍结束 turn；HTML 404 和缺少 mcporter/tool-name 日志标记与此一致。置信度：0.86。
2. **高：Commander 运行时的 CLI 执行策略未知或不允许启动 mcporter。** “已安装”和“已注册”只证明文件/注册表状态，不证明模型可执行该二进制、可继承正确 PATH、可读取工具结果，或可在当前 turn 中运行 shell。置信度：0.78。
3. **中高：更高层系统 prompt 或工具注入覆盖/稀释了 Worker 的 `spec.agents` prompt。** 仓库只保存 Worker prompt，没有可审计的最终 system prompt、注入顺序、优先级或冲突策略；因此 prompt 文本与实际 turn 之间存在未观测层。置信度：0.73。
4. **中：模型调用能力或模型行为本身不稳定。** 活动会话存在但无下游 handoff，可能是模型未选择工具、无法解析调用协议，或在失败响应后提前结束；目前没有模型请求/响应正文，不能进一步区分。置信度：0.55。
5. **低：MCP listener、endpoint 或工具实现仍有基础故障。** 这与双侧 HTTP 200、JSON-RPC、mcporter `status ok` 和当时的本地五工具测试相冲突，仅保留为需后续脱敏调用回执排除的低概率项。该数量是本记录的 point-in-time 事实；后续审批工具加入后当前权威清单为六工具。置信度：0.20。

## 4. 最小修复

1. **先做一次只读运行时能力确认。** 在 Commander 容器内仅检查 `command -v mcporter`、`mcporter --help`、`mcporter call --help`、非执行性的 server/tool 列表摘要，以及最终 Worker system prompt 的来源和优先级；输出只保留存在性、退出码、工具名、版本和错误类别，不保留 URL、账号、房间、请求体或响应体。
2. **把工具纪律下沉到运行时策略。** 允许的子进程仅为已安装的 `mcporter` CLI；禁止任意 curl、浏览器、fetch 和直接 MCP HTTP；工具调用必须返回退出码、结构化 envelope 和同一 trace，失败则标记当前阶段失败，不得生成成功 handoff。
3. **增加代码级阶段门禁和脱敏遥测。** 对每个 Worker 记录 `tool_route=mcporter`、安全工具名、退出码、结果 schema、当前阶段和下一阶段状态；禁止记录请求/响应正文、凭据、房间或其它运行时标识。公开状态只显示 `tool_registered`、`tool_invoked`、`handoff_state` 和脱敏错误类别。
4. **保持 MCP endpoint、Team 成员和模型不变。** 只有在只读能力确认明确证明执行策略或 prompt 注入问题后，才针对四个 Worker 的相应运行时策略做最小变更；不重发 S01 作为验证手段，验证应使用已有合成回放或新的、另行授权的合成测试。

## 5. 修复需要的精确授权

当前诊断未执行修复。若要继续，需用户明确授权以下具体范围：

- 允许对 Commander 及必要时四个 Worker 执行上述只读 `docker exec`/运行时检查；不得读取环境变量、凭据文件、房间/账号标识或原始日志正文。
- 允许修改四个 Worker 的运行时工具执行策略、最终 system prompt 注入规则或对应的安全桥接代码；不得切换模型，不得修改 MCP endpoint、MCP server、Team YAML、凭据或其它 MCP 配置。
- 若运行时变更需要 `apply` 或重启，需另行明确授权“仅重新应用/重启四个 SecTrace Worker”；不得触碰 smoke 资源、Manager、Controller 或真实企业系统。
- 允许使用一次明确限定的合成验证，不等同于发送 S01；发送 S01、人工审批、任何真实处置仍需单独授权。

## 6. 结论

**FAIL**

传输、注册和本地工具实现已有充分正证据，但 Worker 运行时工具策略、mcporter 可执行能力、最终 system prompt 层级和工具注入结果尚未形成可审计闭环；已知的 404 与下游未触发仍然存在。最小修复应先补齐只读能力证据，再获得精确授权后做运行时级门禁，而不是继续扩大 prompt 或网络配置变更。
