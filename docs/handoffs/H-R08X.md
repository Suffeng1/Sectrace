# H-R08X Helper 启动入口诊断交接

日期：2026-08-09

## 已完成

- 同 Manager 镜像、`network=none`、无挂载、`--rm` 的一次性只读 helper 已完成。
- 精确 Node 入口、PATH Node、PATH OpenClaw 均确认可用。
- helper 正常退出并自动删除，残留为 0。
- 未输出路径、配置、凭据、标识、原始 stderr 或日志。

## 结论

入口类别为 `exact_node_available`；先前 `exit 127` 不是镜像缺少执行入口。下一诊断边界是 workspace readonly bind 注入或带挂载的启动上下文。

## 下一项唯一授权建议

授权一次带唯一 workspace readonly bind 的最小 Node helper 门检，仅返回 `node-started`、`config-readable`、`json-parsed` 和旧路径计数，不读取或输出配置内容，不写入，不变更 Manager。
