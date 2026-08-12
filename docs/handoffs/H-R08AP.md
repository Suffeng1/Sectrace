# H-R08AP MCP Transport 诊断交接

日期：2026-08-09

## 结论

`ROOT_CAUSE_CONFIRMED`

第一失败层：`host_mcp_service_absent_or_stopped`

- Existing MCP task exists：true
- Task running：false
- Host MCP process present：false
- Host target listener：false
- 后续 Host TCP/initialize 与 Commander DNS/TCP/initialize：均按短路规则未执行
- 诊断耗时：2.5 秒

该结果足以解释 R-08AO 的 Commander `connection_refused`；未证明或否定防火墙、DNS、路由、bind scope 或协议层，因为 listener 前置门已失败。

## 唯一下一步

单独授权 R-08AQ：仅启动既有精确 MCP 计划任务一次，随后按 Host listener→TCP→initialize→Commander DNS→TCP→initialize 顺序只读复核。不得改配置、重启 Manager/Worker、重发 S01 或处理 smoke。

全部通过后仍需独立的新 S01 单发授权。
