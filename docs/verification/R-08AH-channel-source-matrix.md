# R-08AH Channel 状态来源级错误矩阵

日期：2026-08-09

结论：`ROOT_CAUSE_CONFIRMED`

第一失败层：`global_config_validation_gate`

## 安全边界

- health、channels status、plugins info、config validate 四条公开命令分别独立、有界执行和分类。
- 未合并原始正文后再归因；未读取或输出配置内容、凭据、token、账户/房间/用户/事件标识、原始日志或 stderr。
- 未修改配置，未 enable/disable，未停止或重启 Manager，未发送 S01，未审批、apply/delete 或修改任何资源。

## 命令类别 × 错误类别矩阵

| 命令类别 | completed | exit success | config | auth | pairing | network | room | sync | duplicate plugin | generic |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| health | true | false | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| channels status | true | false | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plugins info | true | false | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| config validate | true | false | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

- Manager running：true
- 诊断窗口：4.1 秒

## 证据与反证

- 四条命令均完成但退出失败，并且各自仅出现配置类错误。这证明它们在进入 channel、插件详情或运行态检查前，共同被全局配置校验门阻断。
- health 的 3 条配置类信号与其它命令各 1 条是按命令分别计数，不能相加后声称存在 6 个唯一配置键。
- config validate 自身退出失败，但 R-08AG 没有发现 Matrix 专属无效 schema 键。因此失败范围应从“Matrix schema 键”修正为“全局配置 schema/结构无效，具体键类别尚未安全投影”。
- 认证、配对、网络、房间订阅与 sync 错误均为 0，原因是初始化链未越过配置门；不能据此声明这些层健康。
- duplicate plugin 错误为 0，保持 R-08AE 的去重修复证据。

## 资格判定

当前不具备单次 S01 preflight 资格。

## 单一最小下一步

建议 R-08AI 仅做纯只读全局 schema 归因：对 config validate 的无效项投影“顶层配置域类别 × 无效键类别 × 唯一计数”，不要求行中出现 Matrix，不输出键名、路径或值。只有确认唯一无效项后，才另行申请精确结构化修复授权。
