# R-08AA Effective Config 位置类别诊断

日期：2026-08-09

结论：`ROOT_CAUSE_CONFIRMED`

## 授权边界

- 仅在运行中 Manager 内进行有界的文件存在性与 Docker 挂载区间比较。
- 未读取或输出配置内容、绝对路径、凭据、标识、原始日志、原始 stderr 或启动脚本。
- 未写入、停止或重启 Manager，未发送 S01，未执行审批、apply/delete 或资源修改。

## 脱敏结果

| 检查项 | 结果 |
|---|---:|
| effective config exists | true |
| relative location category | `standard_openclaw_home_config` |
| storage location category | `manager_workspace_bind` |
| covering mount count | 1 |
| current helper safe readonly access | true |
| path output | false |
| content read | false |
| raw stderr output | false |

## 结论与反证

Effective config 位于 Manager workspace bind，而非 host-share bind、容器镜像层或其它受控挂载。当前 R-08Y helper 的唯一 readonly workspace bind 覆盖该文件，因此具备安全只读访问能力。

这反证了 R-08Z 的“当前 bind 不包含配置”解释。R-08Z 三个布尔为 false 的根因属于 helper 内候选定位或参数传递错误，而不是配置存储位置或 Docker File Sharing 能力。

## 唯一最小修复建议

授权一次同 R-08Y 拓扑的只读预检，但由运行中 Manager 在进程内提供已经验证的 effective config 文件身份给 helper；该身份不得输出或持久化。helper 仅返回 exists/readable/json-parsed 三个布尔，禁止自行拼接候选路径、写入或变更 Manager。
