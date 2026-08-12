# R-08X Helper 启动入口只读诊断

日期：2026-08-09

结论：`COMPLETE`

## 授权边界

- 使用与运行中 Manager 相同的镜像。
- helper 使用 `network=none`、无 workspace 挂载、`--rm`。
- 未读取配置、凭据、标识、原始日志或启动脚本。
- 未停止或重启 Manager，未发送 S01，未执行审批、apply/delete 或资源修改。

## 脱敏验证结果

| 检查项 | 结果 |
|---|---:|
| helper shell started | true |
| Manager 精确 Node 入口在同镜像可执行 | true |
| PATH Node 可用 | true |
| PATH OpenClaw 可用 | true |
| helper 正常退出 | true |
| helper 自动删除、残留为 0 | true |
| 输出路径或原始 stderr | false |

入口分类：`exact_node_available`。

## 诊断结论

先前 `exit 127` 不能归因于 Manager 同镜像缺少精确 Node、PATH Node 或 OpenClaw 执行入口。该反证将故障边界收窄到“带 workspace 只读挂载的 helper 启动参数/挂载上下文”，而不是镜像公开执行能力。

## 唯一下一步

请求一次新的严格只读授权：沿用本次已证明可用的精确 Node 入口，增加唯一 workspace readonly bind，仅执行最小 Node 启动与配置可读性门；不读取配置内容、不写配置、不停止或重启 Manager。该步骤用于区分 Docker bind 注入失败与挂载后启动参数问题。
