# 第二阶段会话执行清单

本文件给 00–05 新会话作为最小任务入口。每个会话必须先读根 `AGENTS.md` 和 `docs/plans/phase-2/README.md`，不得只凭本清单实施。

## 通用开场

```text
你正在正式 SecTrace 仓库执行第二阶段任务。

先读取：
1. 根 AGENTS.md
2. docs/plans/phase-2/README.md
3. docs/plans/phase-2/scoring-traceability.md
4. 当前任务票和上游 Handoff

在任何写入前运行 scripts/sectrace-preflight.ps1 -Mode code。
记录 PLAN_COMMIT、BASE_COMMIT、当前分支和 git status。
只修改 AGENTS.md 分配给本 owner 的文件。
shared contract 问题只写 Handoff 给 00。
不得纳入其他 owner 的修改。
不得执行 runtime mutation、Matrix send/approval、commit 或 push；这些都需要用户单独授权。
严格 RED -> GREEN -> focused tests -> broad tests -> Handoff。
```

## 00：OPT2-00 事实冻结

```text
只处理仓库事实与证据一致性，不修改业务逻辑。

目标：
- 确认远端/本地权威基线；
- 统一真实六工具、RC 测试数字、项目版本与完成态描述；
- 修复或重新指向两个悬空 verification 引用，禁止伪造证据；
- 给旧 Handoff 补 superseded 关系；
- 生成 release-facts 草案。

验证：code preflight、repository hygiene、full pytest、git diff --check、git diff --cached --check、untracked 审计。
交付：owner Handoff；请求 05 独立 QA。
```

## 00：OPT2-01 价值与证据清单

```text
只建立可验证的用户旅程、合成基线、指标目标、行业迁移矩阵和 competition evidence manifest。
不得编造客户、生产数据、效率提升或当前运行状态。
任何缺少用户输入的字段保留明确 TODO，并列为人工事项。
```

## 00：OPT2-02 Eval 核心

```text
实现纯本地、确定性、无 LLM-as-Judge 的 Eval harness。
先将每个指标的 applicable_cases、numerator、denominator、zero policy、evidence source、failure class 写成测试。
数据集不能根据 scenario_id/title/expected 做 oracle 分支；先修复 S02/S03 等语义歧义，增加显式 provenance/corroboration 信号。
00 只写 shared evaluation；01–04 通过 Handoff 提供各角色 oracle；05 只独立运行和写 verification。
```

## 01–04：OPT2-03 各角色 Skill

```text
只修改你拥有的角色和对应 src/skills/<role>/ 目录。
基于现有函数真实签名补 SKILL.md、input/output Schema、CHANGELOG、Golden/Badcase、失败注入、SemVer、发布与回滚说明。
不得新建 MCP 工具、改公开 Contract 或替其他角色写文件。
Evaluation 字段只能引用已经落盘的 OPT2-02 指标。
完成后写本角色 Handoff，交给 00 集成 registry、05 独立 QA。
```

## 02 → 00 → 03 → 04：OPT2-04 分支增强

```text
第一票只能做兼容最小增强：内部 Evidence 三态与 Response 写前 fail-closed。
禁止改公开 Contract、六工具清单或 canonical ledger 精确事件序列。
不得把 blocked-without-Response 的 Audit 状态作为已实现；如确需持久化该分支，先停止并 Handoff 给 00 建 schema-v2 ADR。
re-analysis 最多一次：初始分析不计数，0->1 必须原子，重复/并发/重启不得再次执行。
```

## 00/02：OPT2-05 官方 Skill 条件试点

```text
先做无凭据来源与权限审查，不安装、不联网、不调用。
候选只允许一个阿里云官方只读日志查询 Skill。
检查来源、许可证、依赖、实际命令、是否含写操作、凭据处理和成本边界。
live 验证必须等用户提供 SLS Project/Logstore/index、以本机方式配置最小权限凭据，并对安装/联网/调用分别授权。
不得把凭据写进仓库、prompt、日志、Matrix 或 ledger。
```

## 00：OPT2-06 Identity

```text
从现有生产 YAML、prompt、Team 顺序和 submission Identity 表生成机器可读 manifest，不另创角色语义。
用 contract tests 验 name/role/version/capabilities/I/O/dependencies/permissions/boundaries/trace policy 与生产资源一致。
同时生成 AgentTeams 五项能力映射。
```

## 00：OPT2-08 发布

```text
先冻结 RC0，再生成 release facts；不得在测试前手工写测试数字。
同步 README 与本地 submission，扫描旧工具别名、旧测试数字、本机路径、secret、悬空链接和 future/current 混淆。
记录 PPT/PDF 页数与 SHA-256。
submission 默认不加入 Git。
commit/push 必须另行授权。
```

## 05：独立 QA

```text
你只能写 docs/verification/，不得修业务代码、测试实现、Eval runner、材料或配置。
基于 owner Handoff 独立复现 RED/GREEN、安全边界和 claims。
发现缺陷时写最小复现、第一失败层、影响范围和最小修复建议；交还对应 owner。
历史 FAIL 不删除；新 PASS 必须说明覆盖哪个修订版、不能代表哪些 live/外部事实。
```

## 固定完成报告

```text
STATUS:
PLAN_COMMIT:
BASE_COMMIT:
FINAL_COMMIT: <hash or NO_COMMIT>
FILES_CHANGED:
HANDOFF:
TESTS_RUN:
TEST_RESULT:
NEW_BEHAVIOR:
UNCHANGED_SAFETY_BOUNDARIES:
KNOWN_LIMITATIONS:
NEXT_HANDOFF:
```
