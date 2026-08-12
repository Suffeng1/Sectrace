# H-R08Y 最小只读挂载启动门检交接

日期：2026-08-09

## 结果

- 同 Manager 镜像、精确 Node entrypoint、`network=none`、唯一 workspace readonly bind、`--rm` helper：启动成功。
- 退出类别：`success`。
- 未读取配置、未写入、未输出路径或原始 stderr。
- helper 自动删除，残留为 0。

## 边界收敛

readonly workspace bind 本身不会导致精确 Node 入口失败。先前 `exit 127` 更可能来自当时具体命令参数或瞬态运行上下文，而非镜像入口或挂载能力。

## 唯一下一步

请求一次严格只读配置门检授权：保持相同 helper 拓扑，仅返回配置存在、可读、JSON 可解析的脱敏布尔，不读取输出内容、不写入、不变更 Manager。
