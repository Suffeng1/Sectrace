# R-08AQ MCP Transport 恢复与分层验证

日期：2026-08-09

结论：`TRANSPORT_READY`

## 授权与安全边界

- 唯一运行时写操作是启动 R-08AP 已确认的既有精确 MCP 计划任务一次。
- 未修改任务定义、配置、代码、bind、allowlist、Worker 或 YAML；未使用替代启动方式，未停止或重复启动任务。
- 未重启 Manager/Worker，未发送或重发 S01，未审批、apply/delete，未触碰 `sectrace-smoke`，未 commit/push。
- 未读取或输出秘密、Matrix 标识、地址正文、PID、命令行、路径、响应正文、原始日志、启动脚本或 stderr。

## 写前门与唯一启动

| 检查项 | 结果 |
|---|---:|
| Existing task exists | true |
| Existing task running before call | false |
| Precondition pass | true |
| Task start call count | 1 |
| Task start call success | true |
| Alternate start used | false |
| Task definition changed | false |

## Host 分层验证

| 层 | 结果 | 退出码/类别 |
|---|---:|---|
| Task running after call | true | running |
| Host process present | true | present |
| Target listener present | true | listening |
| Host TCP | pass | 0 |
| Host MCP initialize | pass | 0 |
| Host HTTP category | `2xx` | 成功类 |
| Host protocol category | `mcp_media_type` | MCP 支持媒体类型 |

Host 四门全部通过后才继续 Commander 层。

## Commander 分层验证

| 层 | 结果 | 退出码/类别 |
|---|---:|---|
| Commander running | pass | 唯一运行实例 |
| DNS resolution | pass | 0 |
| TCP connect | pass | 0 |
| MCP initialize | pass | 0 |
| Initialize HTTP category | `2xx` | 成功类 |
| Initialize protocol category | `mcp_media_type` | MCP 支持媒体类型 |

## 结论

R-08AP 确认的 service/listener stopped 状态已通过唯一一次受控启动恢复。Host 与 Commander 的 DNS→TCP→MCP initialize 链全部通过，当前没有 bind、host forwarding、Commander DNS/route 或 MCP endpoint/protocol 的剩余传输阻塞证据。

本票只证明 transport ready，不证明 Manager→Commander→Evidence→Response→Audit 已重新运行，也不证明 pending_approval 或 V-08/V-05 通过。

- First failure layer：none
- 总耗时：5.8 秒
- 响应正文读取：false

## 下一步门

1. 先由 05 对本票的单次启动安全门和 Host/Commander 分层结果做独立 QA；
2. QA PASS 后，仍需用户另行授权一条新的固定合成 S01；不得自动补发 R-08AO 已失败事件；
3. 新单发必须继续固定 `trace_id=tr_s01`、无重试，并在 `pending_approval` 出现时立即停止，绝不自动审批。
