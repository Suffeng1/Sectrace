# R-08AO 手动单发 S01 有界观察

日期：2026-08-09

结论：`STOPPED_AT_MCP_TRANSPORT`

第一可证实失败层：`Commander → SecTrace MCP transport/connectivity`

公开错误类别：`connection_refused`

## 证据边界

- 用户已在正确 Worker ingress 房间，以结构化 Manager mention 单次发送固定合成 S01。
- 本票使用用户现场 UI 截图提供的脱敏人工观察；未索取、读取或复述截图中的 Matrix 标识或消息正文。
- 未读取或输出凭据、token、账户/房间/用户/事件标识、配置正文、原始日志或 stderr。
- 未发送或补发消息，未重试 MCP，未重启、改配置、审批、apply/delete，未修改代码、YAML、MCP、smoke 或 Git。

## 单发锁定

| 检查项 | 结果 |
|---|---:|
| S01 send attempts | 1 |
| automatic retries | 0 |
| auxiliary messages | 0 |
| trace ID | `tr_s01` |
| synthetic/de-identified only | true |

## 脱敏链路状态

| 阶段 | 结果 | 证据类别 |
|---|---:|---|
| Matrix acceptance | true | 下游 Manager 消费构成接受/送达的正向证据 |
| Manager accepted/consumed | true | 用户现场 UI 脱敏人工观察 |
| Manager → Commander routed | true | 用户现场 UI 脱敏人工观察 |
| Commander started | true | 用户现场 UI 脱敏人工观察 |
| Commander preserved `tr_s01` | true | 用户现场 UI 脱敏人工观察 |
| SecTrace MCP call connected | false | transport/connectivity `connection_refused` |
| structured MCP envelope produced | false | 连接在 envelope 产生前失败 |
| Evidence started | false | 安全停止，未继续 handoff |
| Response started | false | 上游未形成 envelope |
| Audit started | false | 上游未形成 envelope |
| four-role same-trace continuity | not reached | 链路停在 Commander→MCP |
| `pending_approval` | false | 未到达 Response 审批门 |

## 首个失败层与反证

本次新证据推翻了继续把阻塞归因于 `manager_consumption` 的历史结论：Manager 已明确消费本次单发 S01，并完成 Manager→Commander 路由。

Commander 已启动并保持 `tr_s01`，但首次 SecTrace MCP 调用在传输连接层被拒绝，未产生结构化 envelope。按照安全规则，Commander 没有虚构结果或继续向 Evidence handoff。因此最早且足以解释全链停止的失败层是：

`Commander → SecTrace MCP transport/connectivity (connection_refused)`。

Evidence、Response、Audit 未启动以及 pending_approval 未出现都是该上游连接失败的预期后果，不能分别登记为新的独立故障。

## 审批门

`pending_approval=false`。本票没有批准或拒绝，也没有任何真实处置。

## 下一项最小授权建议

建议另行授权 R-08AP 纯只读 MCP transport 诊断，严格只检查：

1. 主机既定 MCP 监听端口是否存在监听；
2. 已提交的本地 MCP 服务计划任务/进程是否运行；
3. Commander 容器到既定 `host.docker.internal` MCP endpoint 的 DNS、TCP 与 MCP initialize 分层布尔；
4. 失败分类限定为 listener absent / host bind or firewall / container route / protocol endpoint。

不得在 R-08AP 中启动服务、改 bind/allowlist、重启 Worker、重发 S01 或处理 smoke。确认唯一失败层后再申请精确修复授权。

## QA 请求

请 05 基于本票的脱敏人工 UI 证据独立判断：Manager consumption 与 routing 是否可判通过，以及 `connection_refused` 是否足以把首个失败层定位到 Commander→MCP transport。当前不得把四角色链、pending_approval 或 V-08 判为通过。
