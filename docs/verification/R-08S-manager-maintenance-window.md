# R-08S Manager Stop/Start 维护窗口验证

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：宿主结构化解析
- 安全边界：断言/写入失败立即恢复服务并停止；未发送 S01、未审批、未 apply/delete、未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 维护窗口

- Manager stop 次数：1
- stop 成功：true
- 停止状态确认：true

## Bind 源投影

仅通过 Docker 服务端字段投影取得 Manager workspace bind 源，并在进程内构造 effective config 文件位置：

- bind source 投影成功：true
- effective config 文件可访问：true
- 路径值输出：false

## 结构化补丁结果

宿主 PowerShell JSON 解析器在旧路径计数断言前失败：

- 旧路径匹配计数：未取得
- 结构化写入：false
- 旧路径删除：false
- bundled Matrix enabled 更新：false
- 其它配置值语义验证：未执行

临时文件和原子替换逻辑位于成功解析与计数断言之后，因此本次解析失败没有写入配置或生成补丁。

没有尝试第二种解析器或重试，符合“任一断言/写入失败立即停止”。

## 服务恢复

失败后只执行授权内恢复动作：

- Manager start 次数：1
- Manager running：true

## 未执行事项

- 启动模板复现检查：未执行
- bundled-only：未复核
- duplicate-warning-absent：未复核
- channel-online：未复核
- sync-ready：未复核
- S01/审批：未执行

## 可恢复状态

Manager 已恢复 running，配置未被 R-08S 改写。R-08S 没有留下部分补丁或停止容器。

## 下一项唯一最小授权建议

建议 R-08T 重复同一 stop/start 维护事务，但只替换宿主解析器：

1. 预先只读确认宿主 Node.js JSON 解析器可用；
2. 停止 Manager 一次；
3. 从 Docker 服务端投影相同 bind 源，不输出路径；
4. 使用 Node.js 对同一文件执行与 R-08M 已验证一致的结构化语义补丁：
   - 旧路径精确计数必须为 1；
   - 只删除该项；
   - 仅设置 `plugins.entries.matrix.enabled=true`；
   - 验证其它值语义不变；
5. 启动 Manager 一次；
6. 复核启动模板复现与四项脱敏布尔。

任一门失败仍立即启动恢复并停止。不得在 R-08T 中使用 doctor、读取配置内容或发送 S01。

## 结论

`INCOMPLETE`

当前不能进入 S01 preflight。
