# V-06 R-06 运行时工具策略修复独立验收

## 1. 验收项

- 验收 R-06 运行时工具策略修复及 handoff gate。
- 仅使用合成、脱敏数据；未读取凭据，未发送 S01，未执行审批或真实处置。

## 2. 复现结果

- 非 S01 合成 mcporter 调用退出码：`0`
- 解析路径：`direct_envelope`
- 内层 envelope 字段：齐全
- handoff gate：`True`

## 3. 回归结果

- 仓库回归：`38 passed`

## 4. 检查结论

- 四个 Worker YAML 均包含双路径解析、失败即停规则及显式 `--server/--tool` 调用格式。
- 测试文件包含 7 个显式 `--server/--tool` 调用。

## 5. 结论

PASS
