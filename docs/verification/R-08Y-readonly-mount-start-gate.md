# R-08Y 最小只读挂载启动门检

日期：2026-08-09

结论：`PASS`

## 授权边界

- 使用运行中 Manager 的同一镜像与已确认的精确 Node entrypoint。
- helper 使用 `network=none`、唯一 workspace readonly bind、`--rm`。
- 仅验证 helper 是否正常启动；未读取配置内容，未执行写入。
- 未停止或重启 Manager，未发送 S01，未执行审批、apply/delete 或其它资源操作。

## 脱敏结果

| 检查项 | 结果 |
|---|---:|
| helper started | true |
| exit category | success |
| readonly workspace mount count | 1 |
| config read attempted | false |
| write attempted | false |
| helper auto-removed / residual 0 | true |
| raw stderr output | false |

## 结论

同镜像精确 Node entrypoint 在加入唯一 workspace readonly bind 后仍能正常启动并退出。先前 `exit 127` 不能归因于精确入口缺失，也不能归因于 readonly bind 本身使入口不可执行。

## 唯一安全下一步

另行授权一次同拓扑只读 helper，仅执行结构化的配置文件存在、可读与 JSON 可解析门检，并只返回布尔值；不输出配置内容或路径、不写入、不变更 Manager。
