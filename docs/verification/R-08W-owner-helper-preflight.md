# R-08W File-owner Helper 最终预检

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- Helper 方案状态：停止
- 安全边界：只读 helper；Manager 未停止或重启；未读取或修改配置内容，未发送 S01、未审批、未 apply/delete、未操作其它容器或卷，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始 stderr 或启动脚本，未 commit/push

## Owner 投影

从运行 Manager 内只读取得 effective config 的数字 owner，并只输出类型：

- owner 投影成功：true
- UID 类型：root
- GID 类型：root group
- 数字值输出：false

## Helper 约束

只创建一个精确 helper：

- Manager 当前镜像；
- Manager 内确认的绝对 Node entrypoint；
- 与配置文件相同的 UID/GID；
- `network=none`；
- 唯一 Manager workspace bind；
- mount readonly；
- `--rm`；
- 不写任何文件。

## 四门结果

| 门 | 结果 |
| --- | --- |
| Node 启动 | true |
| config 可读 | false |
| JSON parse | false |
| 旧路径计数 | 未取得（-1） |

helper exit code 为 2。

## 清理与运行态

- helper 自动删除：true
- helper 残留：0
- Manager stop：0
- Manager restart：0

## 最终判断

Helper 方案不具备维护补丁前提，并按授权停止。

R-08V 的 root helper 与 R-08W 的 file-owner helper 得到相同结果；配置 owner 本身也是 root/root。因此问题不是容器内 Unix UID/GID 不匹配，而是 Docker Desktop 对该宿主 bind 的文件访问/隔离策略。

不得继续尝试：

- 其它 UID/GID；
- privileged helper；
- ACL/所有权修改；
- 额外 mount 或 volume；
- Docker copy/导出绕过；
- 重建 helper。

## 下一可行路径

需要用户/操作员在 Codex 之外选择一种方式：

1. 在维护窗口中，由用户本人以有权限的宿主工具对 Manager workspace bind 内的 effective config 执行结构化修改；或
2. 由用户调整 Docker Desktop 对该精确 bind 的文件共享/隔离策略，使宿主或明确授权的 helper 可以访问该单一文件。

用户侧修改必须仍只做：

- 删除旧 Matrix load-path 的唯一数组项；
- 设置 bundled Matrix plugin enabled=true；
- 不运行 doctor，不修改 channel 或凭据值。

完成后，Codex 只需新的只读/启动验证授权：确认旧路径为 0、enabled=true、启动后不复现，并复核 bundled-only、duplicate-warning-absent、channel-online、sync-ready。

## 结论

`INCOMPLETE`

当前不能进入维护补丁或 S01 preflight。
