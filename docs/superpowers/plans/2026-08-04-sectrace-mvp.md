# SecTrace MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` tas&#107;-by-task. Each implementation Ticket is executed by its designated Codex conversation and is independently reviewed by the QA conversation before integration.

**Goal:** Build a safe, executable multi-Agent security-incident audit sandbox for the GOAI Agent Infra track: synthetic incident input is orchestrated through four role-separated Agents into evidence, a human-gated response plan, and a replayable audit report.

**Architecture:** AgentTeams (formerly HiClaw) provides the visible multi-Agent role/orchestration model. A small Python service owns deterministic domain contracts, append-only JSONL ledger events, synthetic scenarios, and read-model reports. The four business Agents only produce structured, schema-validated outputs; no Agent connects to an enterprise system or executes a security action. The UI replays one fixed incident chain by `trace_id`.

**Tech Stack:** AgentTeams/HiClaw; Python 3.11+; FastAPI; Pydantic v2; pytest; SQLite; JSONL; NetworkX; Jinja/HTMX or a minimal React UI selected in ADR-001; Playwright; Git; Codex Security; GitHub Actions only if time remains.

## Global Constraints

- All inputs are synthetic or de-identified. Never add real organization logs, credentials, IP addresses, API keys, or production endpoints.
- The system never scans, attacks, disables accounts, changes permissions, deletes data, or invokes a real remediation API.
- A high-risk response always has `requires_approval: true` and may only be `draft` or `pending_approval`; it can never become `executed` in the MVP.
- Every inter-Agent handoff carries the same `trace_id`, schema version, and ledger references.
- A conclusion must distinguish `fact`, `inference`, and `unknown`; low evidence is reported as “无法确认”, never upgraded into fact.
- AgentTeams (HiClaw) is a hard delivery requirement. The final release must include a real local HiClaw run in which its Manager coordinates the four SecTrace Workers through visible Matrix task communication and a human can inspect/intervene. A compatible local Python adapter may support unit tests, but cannot substitute for this evidence; without the HiClaw run, V-05 is `FAIL`.
- Reuse the four repository Skills below; do not present one-off Python helpers as Skills.
- Project references AiSOC, ESAA-Security, and sample-specship for ideas only. Implement from scratch and record citations in `ADR-003-reference-and-attribution.md`.
- Agents work serially by Ticket; only their declared owned paths may be modified. The control conversation alone changes contracts, specifications, shared application code, configuration, and Git history.

---

## 1. Deliverable and judging evidence

The preliminary submission must be reproducible from the README and show: a business scenario, role decomposition, context passing, state tracking, reusable Skills, security constraints, and evidence of execution. The demonstration uses this fixed path:

```text
异地登录 → 权限提升 → 敏感数据批量访问
→ 证据关联与风险路径 → 待人工审批的处置方案 → 审计报告
```

Required outputs:

```text
README.md                                  # one-command local replay
requirements.md                            # scope and acceptance criteria
CONTEXT.md                                 # stable context sent to all Codex conversations
AGENTS.md                                  # ownership and non-negotiable safety rules
docs/specs/mvp-spec.md                     # product behaviour and non-goals
docs/contracts/system-contract.md          # canonical JSON/Pydantic contracts
docs/adr/ADR-001-agentteams-runtime.md     # AgentTeams mapping and fallback adapter
docs/adr/ADR-002-append-only-audit-ledger.md
docs/adr/ADR-003-reference-and-attribution.md
docs/tickets/*.md                          # executable Ticket boundaries
docs/handoffs/*.md                         # implementation evidence
docs/verification/*.md                     # QA verdicts
docs/status.md                             # sole source of Ticket status
data/scenarios/                            # 24 synthetic JSON cases
outputs/demo/                              # screenshots, video notes, and exported audit bundle
```

## 2. Deliberate tool choices

| Tool / project | Decision | Concrete role |
|---|---|---|
| AgentTeams (formerly HiClaw) | Required; complete Docker/HiClaw preflight in P-01 and demonstrate a real four-Worker run in T-05 | Manager maps Commander, Evidence, Response, Audit Workers and visibly records task assignment, context transfer, state and human review in Matrix rooms |
| Repository Skills + Cloud Skills portal | Required concept; repository Skills are the contest artefacts | `intake.normalize`, `evidence.correlate`, `response.plan`, `audit.verify` each have a stable input/output contract and description |
| Nacos, Higress, PolarDB, RocketMQ | Design for migration; do not deploy in MVP | Respectively future config/service registry, agent/MCP gateway, durable database, event queue. Record adapters in ADR-001/002 |
| SQLite + JSONL | Use in MVP | Simple local state plus append-only replay ledger; zero cloud account dependency |
| NetworkX | Use in MVP | Deterministic evidence relationship/risk path calculation from synthetic events |
| Codex Security | Use at V-05 and before a public demo | Threat model, security scan, evidence-backed finding review; not part of the runtime |
| AiSOC | Borrow concepts only | Ledger, replayability, pseudonymized evidence, confidence/blast-radius/reversibility gating |
| ESAA-Security | Borrow patterns only | JSON Schema boundaries, append-only event store, deterministic report projection, hash replay verification |
| sample-specship | Borrow workflow only | Specification → contract → TDD → adversarial verification → recovery gate |

Do not add Nacos/Higress/PolarDB/RocketMQ merely to name them in the PPT. A documented replacement boundary and a runnable local system scores better than an unconfigured middleware stack.

## 3. Domain contract locked in P-01

All models are Pydantic v2 `BaseModel` models under `src/app/contracts.py`. `schema_version` is `"1.0"` for the MVP.

```python
class IncidentCase(BaseModel):
    trace_id: str
    schema_version: Literal["1.0"]
    scenario_id: str
    severity_hint: Literal["low", "medium", "high"]
    raw_event_refs: list[str]
    tasks: list[Literal["collect_evidence", "plan_response", "audit"]]
    status: Literal["open", "analyzing", "awaiting_approval", "closed"]

class EvidenceItem(BaseModel):
    evidence_id: str
    trace_id: str
    source_ref: str
    statement: str
    classification: Literal["fact", "inference", "unknown"]
    confidence: Literal["low", "medium", "high"]
    evidence_level: Literal["insufficient", "corroborated", "strong"]
    related_event_refs: list[str]

class ResponsePlan(BaseModel):
    plan_id: str
    trace_id: str
    risk_level: Literal["low", "medium", "high"]
    actions: list[str]
    verification_steps: list[str]
    rollback_steps: list[str]
    requires_approval: bool
    status: Literal["draft", "pending_approval", "executed"]

class ApprovalRecord(BaseModel):
    trace_id: str
    approver_role: Literal["human_operator"]
    status: Literal["not_requested", "pending", "approved", "rejected"]
    timestamp: datetime | None

class AuditBundle(BaseModel):
    trace_id: str
    evidence_refs: list[str]
    response_plan_ref: str | None
    approval_ref: str | None
    missing_requirements: list[str]
    report_markdown: str
    ledger_hash: str
```

Ledger records use JSONL with the exact shape:

```json
{"event_id":"evt_001","trace_id":"tr_demo_001","at":"2026-08-04T09:00:00Z","actor":"commander","event_type":"incident.created","payload_ref":"incident:tr_demo_001","prev_hash":"","hash":"sha256..."}
```

`hash` is SHA-256 of canonical JSON for the record excluding its own `hash`, prefixed by `prev_hash`. The report is a deterministic projection from validated ledger events; it is not an unconstrained LLM narrative.

## 4. Repository map and ownership

```text
src/app/                         # 00 only: contracts, ledger, service, orchestration adapter
src/ui/                          # 00 only: demo UI
src/agents/commander/            # 01 only
src/agents/evidence/             # 02 only
src/agents/response/             # 03 only
src/agents/audit/                # 04 only
src/skills/intake/               # 01 only
src/skills/evidence/             # 02 only
src/skills/response/             # 03 only
src/skills/audit/                # 04 only
tests/                           # Agent owns only matching `tests/<agent>/`; 00 owns integration tests
docs/specs/, docs/contracts/, docs/tickets/, docs/adr/, docs/status.md
                                # 00 only
docs/handoffs/H-Txx-*.md         # Ticket implementer only
docs/verification/V-Txx.md       # 05 only
```

Any implementer who finds a contract problem writes it under “需要主控修改 Contract” in the Handoff and stops at that boundary. They do not edit a shared contract.

## 5. Context, state, and Skill story for the competition

SecTrace demonstrates at least three context mechanisms:

1. **Shared structured state:** Pydantic domain objects passed by `trace_id` through AgentTeams task context.
2. **Append-only memory:** JSONL ledger stores each normalized event, decision, approval state, and output reference.
3. **Evidence retrieval:** Evidence Agent retrieves only scenario-local synthetic events from SQLite/JSONL by case and `trace_id`.

The four reusable Skills are repository artefacts with `README.md`, input/output schemas, safety constraints, and tests:

| Skill | Input | Output | Safety rule |
|---|---|---|---|
| `intake.normalize` | synthetic alert/log bundle | normalized event list + `IncidentCase` | rejects an input marked `real_data: true` |
| `evidence.correlate` | `IncidentCase` + event refs | `EvidenceItem` list + risk path | must emit `unknown`/“无法确认” when corroboration is absent |
| `response.plan` | evidence list | `ResponsePlan` | never calls an action API; high risk remains pending approval |
| `audit.verify` | ledger + evidence + plan + approval | `AuditBundle` | redacts secrets and identifies missing evidence/approval |

## 6. Synthetic evaluation suite

Create 24 JSON scenarios, each with expected contract-level assertions. No case contains live credentials or a real organization identifier.

| Group | IDs | Expected outcome |
|---|---|---|
| Main chain | S01–S04 | anomaly login, privilege elevation, mass data access, linked high-risk evidence |
| Incomplete evidence | S05–S08 | `unknown` conclusion or `insufficient` evidence level |
| Malformed/unsafe input | S09–S12 | intake rejects missing field, invalid timestamp, `real_data: true`, unsupported event type |
| Low/medium risk | S13–S16 | review-oriented response plan; no false high-risk claim |
| Approval gates | S17–S20 | high-risk plan is pending; no approval never yields `executed` |
| Audit integrity | S21–S24 | missing evidence/approval flagged, sensitive strings redacted, tampered hash detected, replay stable |

`S01` is the on-stage case. Snapshot tests compare stable structured fields, never an unconstrained natural-language paragraph.

## 7. Ticket sequence and gates

```text
P-00 → P-01 → T-01 → V-01 → integrate/commit
     → T-02 → V-02 → integrate/commit
     → T-03 → V-03 → integrate/commit
     → T-04 → V-04 → integrate/commit
     → T-05 → V-05 → release candidate
```

No code Ticket starts until its predecessor’s verification file says `PASS`. A `FAIL` returns to the same implementation conversation with the QA reproduction steps; a `SPEC-BLOCKED` returns to 00 for contract/specification resolution.

### Task P-00: Project bootstrap and collaboration rules

**Owner:** 00 主控与集成

**Files:**
- Create: `README.md`, `requirements.md`, `CONTEXT.md`, `AGENTS.md`, `.gitignore`, `docs/status.md`
- Create: all directories in Section 4
- Create: `pyproject.toml` with Python 3.11, FastAPI, Pydantic, NetworkX, pytest and Playwright test dependencies only

- [ ] Create the repository skeleton and write the ownership table verbatim into `AGENTS.md`.
- [ ] Initialize Git and create branch `codex/sectrace-bootstrap`; do not commit generated caches, virtual environments, `.env`, SQLite databases, or `outputs/demo` videos.
- [ ] Set `docs/status.md` to `P-00: DONE; P-01: READY; T-01..T-05: BLOCKED`.
- [ ] Run `git status --short` and verify only intentional bootstrap files are present.
- [ ] Commit with `chore: bootstrap SecTrace collaboration workspace`.

**Gate:** a new Codex conversation can identify its owned paths without reading chat history.

### Task P-01: Specification, contracts, architecture decisions, and cases

**Owner:** 00 主控与集成

**Files:**
- Create: `docs/specs/mvp-spec.md`, `docs/contracts/system-contract.md`
- Create: `docs/adr/ADR-001-agentteams-runtime.md`, `ADR-002-append-only-audit-ledger.md`, `ADR-003-reference-and-attribution.md`
- Create: `docs/tickets/T-01-事件指挥.md` through `T-05-集成演示.md`
- Create: `data/scenarios/S01.json` through `S24.json`
- Create: `tests/contracts/test_contracts.py`

- [ ] Use `superpowers:writing-plans`, `domain-modeling`, `api-and-interface-design`, and `architecture-decision-records` to lock the Section 3 models without implementing Agent internals.
- [ ] Run the HiClaw preflight: `docker version`, confirm Docker Desktop has at least 2 CPU cores and 4 GB RAM available, then record the result and the configured local manager URL in ADR-001. Do not install Docker Desktop or enter an LLM key without the user performing those actions.
- [ ] In ADR-001, map each product Agent to a named HiClaw Worker, define its Manager task message, Matrix context fields, completion event, and human approval boundary. State the exact command used to start HiClaw and the required T-05 evidence: Manager page, four Workers, one S01 task chain, and a human-intervention/approval record.
- [ ] In ADR-002, define canonical JSON, the hash calculation, replay verification, and redaction before code begins.
- [ ] In ADR-003, cite AiSOC, ESAA-Security, and sample-specship as conceptual sources and state “no source copied”.
- [ ] Write `test_contracts.py` first to parse one valid `IncidentCase` and reject `ResponsePlan(risk_level="high", requires_approval=False)`.
- [ ] Run `pytest tests/contracts/test_contracts.py -v`; it must fail before models exist, then pass after only contract code is added.
- [ ] Commit with `docs: specify SecTrace MVP contracts and tickets`.

**Gate:** all four implementation Tickets name exact consumed and produced models, and S01 is valid against the contract.

### Task T-01: Event Commander Agent

**Owner:** 01 事件指挥; **Skill:** `superpowers:test-driven-development`

**Files:**
- Create: `src/agents/commander/service.py`, `src/skills/intake/README.md`, `src/skills/intake/normalize.py`
- Create: `tests/commander/test_service.py`, `tests/commander/test_normalize.py`
- Create: `docs/handoffs/H-T01-事件指挥.md`

**Interface:** `build_incident(events: list[dict]) -> IncidentCase`; consumer is Evidence Agent.

- [ ] Write `test_build_incident_from_s01` asserting nonempty `trace_id`, `status == "open"`, and exactly `collect_evidence`, `plan_response`, `audit` tasks.
- [ ] Run `pytest tests/commander/test_service.py::test_build_incident_from_s01 -v`; record its missing-function failure.
- [ ] Implement only synthetic input validation, trace ID creation, event references, and task decomposition.
- [ ] Write `test_rejects_real_data_marker` for `{"real_data": true}` and return a validation error.
- [ ] Run `pytest tests/commander -v` and write the Handoff using Section 8’s template.

**Gate:** no root-cause conclusion and no action execution appears in module text, output, or tests.

### Task V-01: Commander verification

**Owner:** 05 独立 QA; **Skills:** `superpowers:verification-before-completion`, `code-review`

- [ ] Re-run the declared Commander tests, inspect the first failing-test evidence, and check only owned paths changed.
- [ ] Replay S01 and S09; assert S01 produces `IncidentCase`, S09 is rejected, and both produce no remediation call.
- [ ] Write `docs/verification/V-T01.md` with a `PASS`, `FAIL`, or `SPEC-BLOCKED` verdict.

### Task T-02: Evidence Analyst Agent

**Owner:** 02 证据分析; **Skills:** `superpowers:test-driven-development`, `agent-eval`

**Files:**
- Create: `src/agents/evidence/service.py`, `src/skills/evidence/README.md`, `src/skills/evidence/correlate.py`
- Create: `tests/evidence/test_service.py`, `tests/evidence/test_insufficient.py`
- Create: `docs/handoffs/H-T02-证据分析.md`

**Interface:** `analyze(incident: IncidentCase, events: list[dict]) -> list[EvidenceItem]`; consumer is Response Agent.

- [ ] Write `test_s01_has_sourced_fact_and_risk_path` requiring at least one `fact` item with a `source_ref` and a linked privilege-to-data-access path.
- [ ] Run the individual test and record the expected pre-implementation failure.
- [ ] Implement normalization and deterministic NetworkX relations using only supplied synthetic event refs.
- [ ] Write `test_incomplete_case_returns_unknown` using S05 and requiring `classification == "unknown"` plus `evidence_level == "insufficient"`.
- [ ] Run `pytest tests/evidence -v`; write the Handoff.

**Gate:** inferred statements cannot have `evidence_level == "strong"` without two distinct event refs.

### Task V-02: Evidence verification

**Owner:** 05 独立 QA

- [ ] Re-run the evidence tests and test S01/S05 manually through the public function.
- [ ] Confirm each statement has a source, uncertainty is visible, and no external log connector exists.
- [ ] Write `docs/verification/V-T02.md`.

### Task T-03: Response Planner Agent

**Owner:** 03 处置规划; **Skill:** `superpowers:test-driven-development`

**Files:**
- Create: `src/agents/response/service.py`, `src/skills/response/README.md`, `src/skills/response/plan.py`
- Create: `tests/response/test_service.py`, `tests/response/test_approval_gate.py`
- Create: `docs/handoffs/H-T03-处置规划.md`

**Interface:** `plan_response(evidence: list[EvidenceItem]) -> ResponsePlan`; consumer is Audit Agent.

- [ ] Write `test_high_risk_plan_requires_human_approval` using high-risk S01 evidence and asserting `requires_approval is True` and `status == "pending_approval"`.
- [ ] Run it before implementation and record failure.
- [ ] Implement advice-only containment suggestions, verification steps, rollback steps, and risk classification from evidence confidence, blast radius, and reversibility.
- [ ] Write `test_no_approval_can_never_be_executed` and assert the constructor/service rejects an executed high-risk plan.
- [ ] Run `pytest tests/response -v`; write the Handoff.

**Gate:** the source must contain no HTTP client, shell invocation, cloud SDK, account-disable, delete, or permission-change operation.

### Task V-03: Response verification

**Owner:** 05 独立 QA

- [ ] Re-run response tests; grep owned paths for action execution APIs and inspect the result.
- [ ] Verify high-risk S01 is pending approval and a missing approval cannot become executed.
- [ ] Write `docs/verification/V-T03.md`.

### Task T-04: Audit Verifier Agent and replay ledger

**Owner:** 04 审计复核; **Skill:** `superpowers:test-driven-development`

**Files:**
- Create: `src/agents/audit/service.py`, `src/skills/audit/README.md`, `src/skills/audit/verify.py`
- Create: `tests/audit/test_service.py`, `tests/audit/test_redaction.py`, `tests/audit/test_integrity.py`
- Create: `docs/handoffs/H-T04-审计复核.md`

**Interface:** `build_audit_bundle(incident, evidence, plan, approval, ledger) -> AuditBundle`.

- [ ] Write `test_high_risk_without_evidence_or_approval_is_not_qualified`, requiring missing requirements in the audit output.
- [ ] Run it before implementation and record failure.
- [ ] Implement deterministic report projection, evidence/approval completeness checks, and ledger hash verification.
- [ ] Write `test_report_keeps_trace_id_and_redacts_secret` with `API&#95;KEY=secret-value`; assert the report retains trace ID and excludes `secret-value`.
- [ ] Write `test_tampered_ledger_fails_hash_check`.
- [ ] Run `pytest tests/audit -v`; write the Handoff.

**Gate:** no missing item is silently filled, and a tampered ledger is visibly failed.

### Task V-04: Audit verification

**Owner:** 05 独立 QA

- [ ] Re-run all audit tests, tamper with one ledger record in a temporary test copy, and verify the report fails integrity.
- [ ] Confirm sensitive values are absent and missing approvals/evidence are marked.
- [ ] Write `docs/verification/V-T04.md`.

### Task T-05: Integration, AgentTeams mapping, demo UI, and evidence pack

**Owner:** 00 主控与集成; **Skills:** `superpowers:test-driven-development`, `fastapi-patterns`, `frontend-ui-engineering`, `e2e-testing`

**Files:**
- Create: `src/app/ledger.py`, `src/app/orchestrator.py`, `src/app/main.py`, `src/app/agentteams_adapter.py`
- Create: `src/ui/` implementation and `tests/integration/test_s01_flow.py`, `tests/e2e/test_demo_flow.py`
- Modify: `README.md`, `requirements.md`, `docs/status.md`
- Create: `outputs/demo/demo-script.md`, `outputs/demo/evidence-index.md`

- [ ] Write `test_s01_flow_keeps_one_trace_id` asserting Commander → Evidence → Response → Audit return the same trace ID and S01 ends `pending_approval`.
- [ ] Run it before orchestration exists and record failure.
- [ ] Implement only a local deterministic orchestration adapter that calls the four completed interfaces and appends ledger events.
- [ ] Configure the real local HiClaw Manager and create four named Workers for Commander, Evidence, Response, and Audit per ADR-001. Run S01 through the Manager, preserve the visible Matrix conversation/task records, perform one human approval interaction, and save the exact startup/run commands plus screenshots or screen recording references in `outputs/demo/evidence-index.md`.
- [ ] Build a single-screen UI: select S01, run/replay, see four Agent stages, evidence labels, pending human approval, and audit integrity status.
- [ ] Write a Playwright test that selects S01 and sees `待人工审批` plus the trace ID.
- [ ] Run `pytest -v` and the Playwright command documented in README.
- [ ] Commit with `feat: integrate SecTrace audited incident demo`.

**Gate:** a judge can run one documented command, select S01, and see four role outputs, shared trace state, non-executing high-risk plan, and replayable report.

### Task V-05: Release verification and competition artefacts

**Owner:** 05 独立 QA; **Skills:** `superpowers:verification-before-completion`, `agent-architecture-audit`, `ai-regression-testing`, `e2e-testing`, `codex-security:threat-model`, `codex-security:security-diff-scan`

- [ ] Run all unit, integration, and browser tests from a clean environment following README only.
- [ ] Run S01–S24 and write a result matrix with expected/actual outcome in `docs/verification/V-T05.md`.
- [ ] Verify Agent role separation, context handoff, Skill interfaces, ledger replay/hash checks, and approval gate against the competition rubric. Confirm real local HiClaw evidence includes the Manager, all four Workers, the S01 trace, Matrix-visible task/context messages, and human approval. If any item is missing, the final verdict is `FAIL`.
- [ ] Run Codex Security threat model and diff scan on the final committed tree; triage only evidence-backed findings and record dispositions.
- [ ] Inspect Git diff and ownership history; reject unreviewed shared-contract edits or unrelated dependencies.
- [ ] Verify the evidence pack has input, output, activation method, dependencies, failure behavior, safety boundary, reuse story, screenshots, and a 3–5 minute demo script.
- [ ] Set the final verdict to `PASS`, `FAIL`, or `SPEC-BLOCKED`; only `PASS` permits submission packaging.

## 8. Handoff and verification templates

Every implementing conversation creates exactly one handoff:

```markdown
# Handoff: T-xx

- 角色：
- Ticket：
- 修改文件：
- 使用的 Contract 版本：1.0
- 已执行测试：
- 测试输出摘要：
- 主线示例输入：
- 主线示例输出：
- 已知限制：
- 需要 QA 重点检查：
- 是否请求主控修改 Contract：否 / 是（写明字段与原因）
```

QA creates exactly one corresponding verification record:

```markdown
# Verification: T-xx

| 检查项 | 结果 | 证据 |
|---|---|---|
| Ticket 成功标准 | PASS / FAIL | |
| 测试是否真实运行 | PASS / FAIL | |
| 文件所有权是否遵守 | PASS / FAIL | |
| 高风险动作是否被拦截 | PASS / FAIL | |
| 账本、证据和审批边界是否完整 | PASS / FAIL | |
| 是否可交给主控集成 | PASS / FAIL | |

## 问题清单

## 最终结论

仅可填写：PASS / FAIL / SPEC-BLOCKED
```

## 9. Six Codex conversations: final prompts

All conversations work in `<repo-root>`. Start only the listed conversation for the current Ticket. Do not run implementation conversations in parallel.

### 00 — SecTrace 主控与集成

```text
你是 SecTrace 的主控与集成 Agent。当前工作目录必须是 project_005_SecTrace安全事件多Agent协同审计系统。

先阅读 AGENTS.md、README.md、requirements.md、CONTEXT.md、docs/ 目录和 docs/superpowers/plans/2026-08-04-sectrace-mvp.md。

系统是“安全事件多 Agent 协同审计演练系统”：只使用合成或脱敏数据；不攻击、扫描或连接真实系统；高风险动作只生成待人工审批方案；四个业务 Agent 是事件指挥、证据分析、处置规划、审计复核。

比赛约束：AgentTeams（原 Hiclaw）是硬性必选项。P-01 必须完成 Docker/HiClaw 预检；T-05 必须在真实本地 HiClaw Manager 下建立四个 Worker 并运行 S01，保留 Matrix 中可见的角色编排、任务拆分、上下文传递、状态追踪和人工审批证据。Python 本地适配器只能辅助单元测试，不能替代 HiClaw 证据。每一步用 trace_id 和追加式 JSONL Ledger 留痕。参考 AiSOC、ESAA-Security、sample-specship 的思想但禁止复制源码，并维护 ADR-003。

你的独占范围：根目录、src/app/、src/ui/、项目配置、docs/specs/、docs/contracts/、docs/tickets/、docs/adr/、docs/status.md 和 Git。
不得实现四个业务 Agent 内部逻辑。

使用 superpowers:writing-plans、api-and-interface-design、domain-modeling、architecture-decision-records；按计划书只执行我指定的 P-00、P-01 或 T-05。QA PASS 前不得集成或提交对应 Ticket。每次完成后更新 docs/status.md 并说明下一个可执行 Ticket。
```

### 01 — SecTrace 事件指挥

```text
你是 SecTrace 的事件指挥 Agent 实现者。先阅读 AGENTS.md、CONTEXT.md、mvp-spec、system-contract、T-01、status 和最终执行计划书。

你的独占范围：src/agents/commander/、src/skills/intake/、tests/commander/、docs/handoffs/H-T01-事件指挥.md。禁止修改 Contract、Spec、Ticket、配置、Git 或任何其他 Agent 目录。

必须使用 superpowers:test-driven-development：先为 S01 写失败测试并运行确认失败；最小实现 `build_incident(events) -> IncidentCase`；再写 `real_data: true` 拒绝测试；全部通过后写 Handoff，等待 QA。

必须维护 AgentTeams 可见的角色任务、trace_id 和任务拆分；不判断根因、不执行处置、不处理真实数据。当前只执行 T-01。
```

### 02 — SecTrace 证据分析

```text
你是 SecTrace 的证据分析 Agent 实现者。先阅读 AGENTS.md、CONTEXT.md、mvp-spec、system-contract、T-02、status、H-T01 和 V-T01，以及最终执行计划书。

你的独占范围：src/agents/evidence/、src/skills/evidence/、tests/evidence/、docs/handoffs/H-T02-证据分析.md。禁止修改共享 Contract、其他 Agent、配置、Spec、Ticket 和 Git。

使用 superpowers:test-driven-development 与 agent-eval：先写并运行失败测试，要求 S01 IncidentCase 返回至少一条有 source_ref 的事实证据和风险路径；最小实现事件标准化、NetworkX 关系分析、证据等级；再为 S05 写证据不足测试，必须输出 unknown/insufficient/“无法确认”。测试通过后写 Handoff，等待 QA。

只分析输入的合成事件，不连接真实日志；推测不得包装为事实。当前只执行 T-02。
```

### 03 — SecTrace 处置规划

```text
你是 SecTrace 的处置规划 Agent 实现者。先阅读 AGENTS.md、CONTEXT.md、mvp-spec、system-contract、T-03、status、H-T02 和 V-T02，以及最终执行计划书。

你的独占范围：src/agents/response/、src/skills/response/、tests/response/、docs/handoffs/H-T03-处置规划.md。禁止修改共享 Contract、其他 Agent、配置、Spec、Ticket 和 Git。

必须使用 superpowers:test-driven-development：先写并运行失败测试，要求高风险 S01 EvidenceItem 产生 `requires_approval=true`、`status=pending_approval` 的 ResponsePlan；最小实现风险分级、建议、验证和回滚步骤；再测试未人工批准时绝不产生 executed 状态。测试通过后写 Handoff，等待 QA。

策略输入必须考虑证据置信度、影响范围和可逆性。不得调用任何禁用账号、删除数据、修改权限或真实 API 的能力。当前只执行 T-03。
```

### 04 — SecTrace 审计复核

```text
你是 SecTrace 的审计复核 Agent 实现者。先阅读 AGENTS.md、CONTEXT.md、mvp-spec、system-contract、T-04、status、H-T03 和 V-T03，以及最终执行计划书。

你的独占范围：src/agents/audit/、src/skills/audit/、tests/audit/、docs/handoffs/H-T04-审计复核.md。禁止修改共享 Contract、其他 Agent、配置、Spec、Ticket 和 Git。

必须使用 superpowers:test-driven-development：先写并运行失败测试，要求缺少 EvidenceItem 或审批记录的高风险 ResponsePlan 不能生成合格审计包；最小实现确定性报告投影、证据/审批检查和 Ledger 哈希校验；再测试 trace_id 保留、API Key 脱敏以及 Ledger 篡改失败。测试通过后写 Handoff，等待 QA。

不伪造证据、不泄露原始敏感数据；缺失项必须显式标记。当前只执行 T-04。
```

### 05 — SecTrace 独立 QA

```text
你是 SecTrace 的独立 QA Agent。你只验收并写 docs/verification/，绝不修改业务代码。

先阅读 AGENTS.md、CONTEXT.md、mvp-spec、system-contract、当前 Ticket、对应 Handoff、README、Git diff、相关源码与测试，以及最终执行计划书。

使用 superpowers:verification-before-completion；发现问题使用 superpowers:systematic-debugging（复现→缩小范围→证据→原因假设→退回建议）。在 V-05 还要使用 agent-architecture-audit、ai-regression-testing、e2e-testing 和 Codex Security 的 threat-model/security-diff-scan。

逐项对照 Ticket，真实运行实现者声称的测试，检查先失败后通过的证据、文件所有权、无真实数据、无自动高风险执行、无伪造证据、Ledger 回放/哈希与审批边界。V-05 还必须核验真实 HiClaw Manager、四个 Worker、S01 Matrix 任务链和人工审批记录；缺一项即 FAIL。写 V-Txx，结论只能是 PASS、FAIL 或 SPEC-BLOCKED；不得口头放行或代替实现者修代码。
```

## 10. Operator checklist

1. Start 00 and send its prompt; run P-00.
2. In the same 00 conversation send: `执行 P-01，只写规格、契约、ADR、24 个合成案例和 T-01 到 T-05，不写业务 Agent。` 
3. Start 01 only after P-01 is committed; run T-01, then start 05 for V-01.
4. If V-01 is PASS, tell 00: `集成 T-01，并依据 V-T01 提交 Git；然后将 T-02 标记 READY。`
5. Repeat `02 → 05 → 00`, then `03 → 05 → 00`, then `04 → 05 → 00`.
6. Tell 00 to run T-05 only after V-T04 is PASS; then let 05 run V-T05.
7. Do not submit until V-T05 is PASS and `outputs/demo/evidence-index.md` supports every competition claim.

## 11. Plan self-review

- **Competition coverage:** scenario, four roles, AgentTeams mapping, context/state, reusable Skills, human approval, audit/replay, and evidence pack are each assigned to P-01, T-01–T-05, or V-05.
- **Safety coverage:** synthetic-only input, no execution, approval gate, uncertainty labels, redaction, hash verification, and security scan have executable gates.
- **Scope control:** enterprise middleware is represented by migration boundaries rather than premature deployment.
- **Collaboration coverage:** every code Ticket has a single owner, a written Handoff, an independent QA verdict, and a main-control integration gate.
