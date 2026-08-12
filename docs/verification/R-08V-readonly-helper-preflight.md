# R-08V Read-only Helper 预检

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：helper bind 文件可读性
- 安全边界：只读 helper；Manager 未停止或重启；未读取或修改配置内容，未发送 S01、未审批、未 apply/delete、未操作其它容器或卷，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始 stderr 或启动脚本，未 commit/push

## Node Entry Point

从运行 Manager 中只读解析 Node：

- Node 规范路径为绝对路径：true
- 路径类型：system tree
- 路径值输出：false

## Helper 约束

只创建一个精确 helper：

- Manager 当前镜像；
- root 用户；
- Manager 内确认的绝对 Node entrypoint；
- `network=none`；
- 唯一 Manager workspace bind mount；
- mount 显式 readonly；
- `--rm`；
- 不写任何文件。

## 四个预检门

| 门 | 结果 |
| --- | --- |
| Node 启动 | true |
| config 可读 | false |
| JSON parse | false |
| 旧路径计数 | 未取得（-1） |

helper exit code 为 2。没有输出原始 stderr 或配置/路径内容。

## 清理与运行态

- helper 自动删除：true
- helper 残留：0
- Manager 停止次数：0
- Manager 重启次数：0

## 判断

不具备维护补丁前提。

R-08U 的失败不是相对 Node entrypoint 导致；R-08V 已证明绝对 Node 可正常启动。失败点是 Docker Desktop bind 的权限映射：helper root 身份不能读取该文件。

## 下一项唯一最小授权建议

建议 R-08W 仍先做只读预检：

1. 从运行 Manager 内只读取得 effective config 文件的数字 owner UID/GID，只输出“存在”和用户类型，不输出其它元数据；
2. 用相同镜像、绝对 Node entrypoint、`network=none`、readonly 唯一 workspace mount、`--user <owner uid>:<owner gid>` 创建一次 `--rm` helper；
3. 仅验证 Node、config readable、JSON parse、旧路径计数；
4. 不停止 Manager、不写配置。

如果 file-owner helper 仍不可读，应停止 helper 方案，由用户本人调整宿主 ACL 或离线修改。不得自动尝试 privileged、ACL 修改或额外 mount。

## 结论

`INCOMPLETE`

当前不能进入维护补丁或 S01 preflight。
