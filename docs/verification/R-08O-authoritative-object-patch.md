# R-08O Authority Object Patch 验证

- 日期：2026-08-09
- 结论：`INCOMPLETE`
- 停止层：watcher 方向断言
- 安全边界：断言失败立即停止；未写权威对象、未执行 enable、未重启 Manager、未发送 S01 或审批，未修改 Worker/YAML/业务代码/MCP，未 apply/delete，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 精确暂停与上下文分类

1. 精确找到 R-08N 识别的对象存储同步子进程。
2. 对该单一进程发送 pause。
3. 只在进程内解析参数类型，不输出参数值。
4. Manager workspace 端与对象存储 alias 端都存在。

必须满足的方向断言为：

`对象存储源 → Manager workspace 目标`

实际方向断言：

- 对象存储端存在：true
- Manager workspace 端存在：true
- 对象存储端位于 workspace 端之前：false

因此实际进程方向是：

`Manager workspace → 对象存储`

该进程是出站同步 watcher，不是把权威副本恢复到本地 workspace 的入站 watcher。

## 失败停止与回滚

方向断言失败后：

- 未读取对象内容；
- 未定位或输出对象路径值；
- 未执行断言/删除旧 load-path；
- 未写回任何对象；
- 未执行 `openclaw plugins enable matrix`；
- Manager 重启次数：0；
- 四布尔未复核。

只执行授权允许的失败回滚：恢复同一 watcher。只读复核确认 watcher 存在且不再处于 paused 状态。

## 对 R-08N 的修正

R-08N 将长期对象存储子进程判定为本地持续写入者，证据不足。R-08O 的参数顺序类型提供了直接反证：

- 该 watcher 从 Manager workspace 向对象存储同步；
- 它可以把本地状态上传为远端副本；
- 它不能解释“本地精确删除后、下一 CLI 前旧路径在本地重新出现”。

因此 R-08N 的唯一写入者结论被本文件取代。

## 当前剩余假设

按优先级：

1. OpenClaw CLI 在启动/插件发现阶段从 registry 或镜像插件元数据重建 effective `plugins.load.paths`；
2. CLI 实际解析的 HOME/config 路径与 R-08M 结构化编辑的路径不一致或存在链接/层叠配置；
3. Manager PID 1 supervisor 在本地重写配置；
4. Controller 通过非共享文件系统的 API 协调配置。

## 下一项唯一最小授权建议

建议 R-08P 仅做只读定位：

1. 比较 OpenClaw CLI effective config 的规范化路径类型与 R-08M 编辑目标是否为同一文件，只输出布尔值；
2. 分别判断旧 load-path 当前存在于：
   - effective JSON 文件；
   - OpenClaw persisted plugin registry；
   - CLI 冷启动派生视图；
3. 只输出来源类别和匹配计数，不读取或输出其它配置值、参数、凭据、标识或日志；
4. 不暂停进程，不修改或重启。

确认唯一来源后，再单独授权修复。当前不能继续重复本地删除、对象补丁或 enable。

## 结论

`INCOMPLETE`

R-08O 未通过方向断言，不能进入 S01 preflight。
