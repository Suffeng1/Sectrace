# R-08T Host Node.js 维护补丁验证

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：宿主文件访问权限
- 安全边界：失败立即启动恢复并停止；未发送 S01、未审批、未 apply/delete、未删除容器或卷，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 宿主 Node.js 门

- 宿主 Node.js 可用：true
- 版本信息存在：true

## 维护窗口

- Manager stop 次数：1
- Manager stopped：true
- Docker bind 源投影成功：true
- effective config 文件路径存在：true
- 路径值输出：false

## 结构化补丁结果

宿主 Node.js 在读取 effective config 文件的第一步收到操作系统 `EACCES`：

- JSON 读取：失败
- 旧路径计数断言：未执行
- 临时文件创建：未执行
- 配置替换：未执行
- bundled Matrix enabled 更新：未执行
- 语义验证：未执行

因此不存在部分写入或临时补丁。

按照失败门，没有：

- 修改宿主 ACL/所有权；
- 申请额外文件权限；
- 复制配置到临时位置；
- 使用其它解析器；
- 重试。

## 服务恢复

- Manager start 次数：1
- Manager running：true

## 未执行验收

- 启动模板复现检查：未执行
- bundled-only：未复核
- duplicate-warning-absent：未复核
- channel-online：未复核
- sync-ready：未复核

## 可恢复状态

Manager 已恢复 running，配置未被 R-08T 读取或改写。R-08T 没有改变文件权限、容器或卷。

## 下一项唯一最小授权建议

建议 R-08U 使用一次精确的 root 权限临时 helper 容器，而不修改宿主 ACL：

1. 停止 Manager 一次；
2. 通过 Docker 服务端投影取得 Manager 当前镜像引用与 workspace bind 源，不输出值；
3. 使用该镜像、显式 `node` entrypoint、只挂载同一 workspace，创建一次无网络、无额外卷的临时 helper；
4. helper 仅执行 R-08T 已定义的结构化补丁和布尔验证；
5. helper 完成后自动删除；
6. 启动 Manager 一次；
7. 复核启动模板复现与四项脱敏布尔。

该方案需要明确授权创建并删除一个精确临时 helper 容器；不得使用 prune，不得访问其它 mount、容器或 volume。若用户不授权临时容器，应由用户本人调整该文件权限或离线修改。

## 结论

`INCOMPLETE`

当前不能进入 S01 preflight。
