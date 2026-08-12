# R-08U Root Helper 维护补丁验证

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：一次性 helper 运行
- 安全边界：失败立即启动 Manager 恢复并停止；未发送 S01、未审批、未 apply/delete、未删除卷或其它容器，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 维护窗口

- 精确 helper 名称预先不存在：true
- Manager stop 次数：1
- Manager stopped：true
- 当前镜像由 Docker 服务端投影：true
- workspace bind 源由 Docker 服务端投影：true
- 镜像与路径值输出：false

## Helper 约束

本轮只创建一个精确 helper：

- 使用 Manager 当前镜像；
- root 用户；
- 显式 Node entrypoint；
- `network=none`；
- 仅一个 Manager workspace bind mount；
- 无额外 mount 或 volume；
- `--rm`。

## Helper 结果

- helper exit code：1
- 结构化补丁摘要：未产生
- helper 自动删除：true
- helper 残留容器：0

由于没有结构化摘要，无法证明 helper 到达旧路径计数断言、JSON 写入或后置验证中的任何阶段。本轮没有读取或输出 helper 原始 stderr，也没有为了分类错误而重建或重试 helper。

不能声称配置已修改，也不能在缺少摘要时声称配置绝对未触及。失败后没有执行启动模板或四布尔探针。

## 服务恢复

- Manager start 次数：1
- Manager running：true

## 未执行验收

- 旧路径启动复现：未检查
- bundled-only：未复核
- duplicate-warning-absent：未复核
- channel-online：未复核
- sync-ready：未复核

## 可恢复状态

- Manager 已恢复 running；
- helper 已自动删除；
- 没有额外容器、mount 或 volume；
- 未执行 prune。

## 下一项唯一最小授权建议

建议 R-08V 先做只读 helper 兼容性探针，不停止 Manager：

1. 从正在运行的 Manager 中只读取得 Node 可执行文件的规范路径类型，不输出路径；
2. 使用同一镜像、该绝对 Node entrypoint、root、`network=none`、相同单一 workspace mount 创建一个 `--rm` helper；
3. helper 只验证：
   - Node 启动成功；
   - effective config 可读；
   - JSON 可解析；
   - 旧路径匹配计数；
4. 不写配置；
5. helper 自动删除。

只有 R-08V 取得完整只读摘要后，才可另行授权新的维护补丁。不得直接重复 R-08U。

## 结论

`INCOMPLETE`

当前不能进入 S01 preflight。
