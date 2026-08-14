# GOAI 评分追踪矩阵

本表依据本地《GOAI参赛指南》评分页建立。执行时仍应以报名平台和赛事群最新正式通知为准。

| 评分项 | 权重 | 当前强项 | 当前缺口 | 第二阶段任务 | 验收证据 | 材料呈现 |
|---|---:|---|---|---|---|---|
| 场景价值与行业可复制性 | 25% | 安全事件跨角色治理场景清晰；可迁移到审计/风控/运维变更 | 无人工基线、用户旅程和量化价值；迁移边界过于概括 | OPT2-01、OPT2-02 | value baseline、Eval report、evidence manifest | 场景痛点、用户旅程、量化目标、行业迁移矩阵 |
| 多 Agent 协同与自主闭环 | 25% | 四 Agent、Manager route-only、typed handoff、trace、人工审批、独立 Audit 已有 live 证据 | AgentTeams 五项能力映射不显式；不足/冲突与多方案选择较弱 | OPT2-04、OPT2-06 | branch tests、Identity contract、AgentTeams mapping | 架构、正常链、异常/冲突策略、平台能力映射 |
| Skill 工程体系与生态复用 | 25% | 四个自有 Skill 有真实 Python 实现与边界 | 无标准 Skill 包、版本、Schema、发布/回滚、质量报告；官方云 Skill 未接 | OPT2-02、OPT2-03、OPT2-05 | Skill registry、schema tests、Eval、官方 Skill只读证明 | 四 Skill Identity、生命周期、评测、一个官方 Skill及限制 |
| 工程落地、运行验证与安全可审计 | 20% | 六 MCP、持久化状态机、哈希账本、Matrix 审批来源校验、preflight、历史 live PASS | 指标/telemetry弱；证据索引有断链；Demo阅读成本高 | OPT2-00、OPT2-02、OPT2-08、OPT2-09 | release facts、tests、Eval、artifact hashes、independent QA | 快速部署、证据入口、安全边界、可复核结果 |
| 开放/开源贡献 | 5% | Apache-2.0、公开仓库、依赖披露 | 需确认默认分支、来源/团队贡献、维护/发布约定 | OPT2-00、OPT2-03、OPT2-08 | anonymous GitHub check、LICENSE、CHANGELOG | 项目来源、贡献边界、许可、复现与路线图 |

## 评分优先级结论

1. 先做价值/Eval/Skill 生命周期，覆盖 75% 核心评分面。
2. 安全与协同已有高质量底座，应补证据入口和异常分支，不重复实现。
3. 官方用云 Skill 的指南口径存在“推荐”与“使用”并存。风险最小方案是接一个只读官方 Skill；若条件不足，必须取得赛事官方答复并诚实披露。
4. OTel、Nacos、更多 Agent、RAG 和大型 UI 改造不是初赛前最高收益项。

## 每项 claim 的证据规则

- `implemented`：代码、测试与可定位证据三者同时存在。
- `verified`：标明版本/commit、命令、结果和适用范围。
- `live verified`：另标 point-in-time，不代表当前运行时。
- `planned`：不得出现在“当前能力”或成绩数字中。
- 外部平台能力必须写清由哪个层提供，不能归功于 SecTrace 核心代码。
- 测试数字只从 RC 命令生成，不手工抄写多个来源。

## 必须人工确认的比赛信息

- 初赛是否硬性要求实际接入阿里云官方用云 Skill。
- PPT/PDF 页数、大小、模板和附件规则的最新口径。
- 项目来源、成员贡献和本次新增创新的正式表述。
- 仓库链接、团队名称、联系人和提交平台元数据。
