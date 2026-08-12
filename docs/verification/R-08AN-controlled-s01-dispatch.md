# R-08AN 一次性受控 S01 诊断发送

日期：2026-08-09

结论：`BLOCKED_PRE_SEND`

第一失败层：`human_sender_session_unavailable`

## 安全边界

- 目标发送必须保持 R-08G 已验证的人类 admin/operator sender、唯一 Manager ingress DM 和唯一 Manager mention。
- 未读取或输出凭据、token、账户/房间/用户/事件标识、消息正文、配置、日志或 stderr。
- 未改配置、Manager、Worker、MCP、代码、YAML、smoke 或 Git；未审批、apply/delete。

## 发送前入口验证

| 检查项 | 结果 |
|---|---:|
| `agent-browser` available | false |
| expected CDP entry reachable | false |
| common local CDP entry count | 0 |
| Element interactive desktop window count | 0 |
| host `agt` available | false |
| Controller running | true |
| Controller `agt` available | true |
| Controller `agt` public help completed | true |
| supported human Matrix ingress send command | false |

Controller 内 `agt` 的公开命令面仅用于 Worker/Team/Human/Manager 资源管理，不提供以当前人类 admin/operator Matrix 会话向 ingress DM 发送消息的命令。使用 Controller 资源 API、Manager 身份或读取 token 自建 Matrix 请求都不能保持 R-08G 的 sender 前提，因此没有采用。

## 发送与观察结果

| 检查项 | 结果 |
|---|---:|
| actual S01 send attempts | 0 |
| automatic retries | 0 |
| auxiliary messages | 0 |
| Matrix acceptance | not attempted |
| Manager consumption | not observed |
| Manager routing | not observed |
| Commander appeared | not observed |
| Evidence appeared | not observed |
| Response appeared | not observed |
| Audit appeared | not observed |
| same-trace continuity | not observed |
| pending_approval | not reached |

由于发送前必要的人类会话入口不可用，没有构造或发送 S01，也没有启动观察窗口。不能把这些 `not observed` 解释为运行时失败。

## 最小人工动作

用户需要在本机打开并保持唯一一个已登录的人类 admin/operator Element/官方 Matrix UI 会话，并使其通过受支持 CDP 入口或唯一可交互桌面窗口可用；不要预先发送任何消息。入口可用后，再由源任务确认一次性授权仍有效并继续同一 R-08AN：固定 `trace_id=tr_s01`、单次发送、无重试，pending_approval 即停。

## QA 请求

请 05 独立确认：本票在无法证明人类 sender 会话的情况下保持零发送是否符合安全门，以及恢复 UI 入口后能否继续同一一次性发送授权。当前不得把 R-08AN 判为 S01 链路通过。
