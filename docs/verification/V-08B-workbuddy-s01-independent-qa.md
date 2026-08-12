# V-08B WorkBuddy S01 Independent QA

- Date: 2026-08-11
- Result: **FAIL**
- Reviewed live-event date: 2026-08-10
- Runtime action: none; Docker was not started and no live replay was attempted
- R-08AX persistence work: explicitly excluded from this verification

## Decision

The 2026-08-10 materials are credible evidence that WorkBuddy observed a successful S01 chain, and they add materially more information than the evidence available to the original V-08. They are not, however, sufficient independent evidence to overturn V-08 from FAIL to PASS.

The central limitation is evidence provenance: the final chain is documented primarily as WorkBuddy narration plus selected message/log excerpts. The repository does not contain a redacted, independently correlatable Matrix/event evidence package for all stages, nor the complete approval-ledger/hash projection needed to verify the claimed `qualified` result without trusting the narrator.

## Evidence classes

### 1. Code-reproducible evidence: PASS

Current R-08B implementation independently confirms:

- `plan_ref` must match the current `ResponsePlan.plan_id`;
- approver and ledger actor are fixed to `human_operator`;
- approval reason is persisted only as SHA-256 reference;
- transitions are one-way from `pending` to `approved/rejected`;
- repeat or override attempts fail before ApprovalRecord or ledger mutation;
- approved and rejected paths are separately exercised;
- high-risk audit qualification requires an approved record while the response plan remains `pending_approval`.

Independent code preflight and tests:

```text
code preflight: READY_CODE
R-08B MCP + Contract + Audit: 19 passed in 0.81s
tracked-repository hygiene core: 1 passed in 0.14s
broad code regression excluding R-08AX and tmp_path hygiene cases: 50 passed in 0.93s
```

An earlier attempt additionally produced 20 passing focused assertions and 51 passing broad assertions, but three `tmp_path` setup errors in each run occurred because the sandbox denied creation of the selected temporary directory. They were environment setup errors, not product assertion failures, and are not presented as a green run.

This code evidence resolves the original V-08 technical findings about missing plan binding, unconstrained approver identity, and reason audit representation.

### 2. WorkBuddy self-attestation: supportive but not independently sufficient

R-08AV-6/7/8 and the WorkBuddy Handoff state that:

- Manager recovered and consumed the S01;
- Commander rebuilt `tr_s01` and delegated Evidence;
- Evidence produced three sourced facts;
- Response produced the high-risk pending plan;
- the user authorized an approval message;
- Commander logged `approval.approved`;
- Audit returned `qualified` with integrity passed.

These claims are internally consistent with the current code and with the described failure/recovery sequence. They remain assertions authored by the same automation/operator that performed or observed the actions.

### 3. Matrix-visible evidence: described, not independently packaged

The records describe UI-visible Manager, Commander, approval, and Audit messages and provide timestamps and selected excerpts. However, the project evidence set does not include a redacted screenshot sequence or structured export that independently establishes:

- distinct Manager, Commander, Evidence, Response, and Audit sender roles;
- one unchanged `tr_s01` across every visible stage;
- the exact pending plan reference before approval;
- the approval event's human sender role and its binding to that plan;
- the final Audit message's correlation to the same ledger and trace.

The only referenced screenshot path is outside the formal project evidence set and concerns room preparation, not the completed four-role/approval/Audit chain. It was not treated as final-chain evidence.

### 4. Missing independent original evidence

The following required artifacts are absent from the repository evidence package:

1. a redacted chronological Matrix screenshot/export covering Manager intake, each distinct Worker handoff, pending approval, human decision, approval-ledger confirmation, and Audit result;
2. stable redacted event/message references that allow the stages to be correlated without exposing Matrix identifiers;
3. a structured projection of the Incident, Evidence items, ResponsePlan, ApprovalRecord, approval ledger record, and AuditBundle showing one `tr_s01` and one `rp_tr_s01` relationship;
4. the canonical approval ledger fields, previous hash, approval record hash, and terminal Audit ledger hash needed to independently verify the claimed hash-chain continuity;
5. independent evidence that the approval action was performed by the user through the allowed human session, rather than merely a statement that WorkBuddy constructed the message and the user authorized its send;
6. response/audit file-handoff artifacts. R-08AV-8 explicitly states that these were not written and that the chain advanced through in-memory MCP/message state.

Because those artifacts are missing, the textual statement `audit_status=qualified` cannot itself prove qualification.

## Acceptance-by-stage assessment

| Requirement | WorkBuddy claim | Independently supportable result |
|---|---|---|
| Manager consumed S01 | yes | **INCOMPLETE** — narration/excerpt only |
| Commander created/rebuilt `tr_s01` | yes | **INCOMPLETE** — no independently packaged envelope |
| Evidence role produced sourced facts | yes | **INCOMPLETE** — no distinct-role Matrix/export artifact |
| Response produced high-risk pending plan | yes | **INCOMPLETE** — no independently packaged ResponsePlan |
| Same trace and plan continuity | yes | **INCOMPLETE** — no cross-stage correlation bundle |
| Approval actor was the user | asserted | **INCOMPLETE** — authorization statement is not independent sender/action proof |
| Approval ledger event and hash continuity | asserted | **INCOMPLETE** — no canonical redacted record/hash chain |
| Audit was qualified/integrity passed | asserted | **INCOMPLETE** — selected text only |
| Role separation | described | **INCOMPLETE** — distinct sender evidence absent |
| Synthetic-only | described and code-compatible | **INCOMPLETE live evidence** — final event set not independently packaged |
| No real execution | described and contract-enforced | **PASS at code level; INCOMPLETE at live-evidence level** |

## Contract and safety assessment

The claimed sequence is compatible with the system Contract: Incident → Evidence → pending ResponsePlan → human ApprovalRecord → AuditBundle. The code prohibits high-risk `executed`, fixes approval identity to `human_operator`, and produces a hashed approval reference.

Compatibility is not proof that the specific live run followed the contract. Without independently reviewable stage envelopes and ledger projection, role separation, human identity, trace continuity, and no-execution for the observed run remain insufficiently evidenced.

## Handoff and status consistency

- `H-R08.md` still records `INCOMPLETE` and says the user has not performed the required new approval.
- R-08AV-8 later claims completion but does not provide the independent artifact package needed to supersede that Handoff safely.
- The old V-08 must remain preserved as historical FAIL; V-08B does not rewrite it.

## R-08AX exclusion

The current worktree contains an untracked persistence test and related in-progress MCP changes. The persistence test expects a `state_dir` constructor not present in the reviewed adapter snapshot, demonstrating that R-08AX is not an integrated, completed baseline. No R-08AX test, persistence behavior, or restart claim is used to pass or fail V-08B.

## Minimum evidence needed to re-evaluate V-08

No new S01 is automatically required if the 8/10 evidence can be recovered safely. The minimum acceptable package is:

1. redacted chronological screenshots or a safe structured export showing distinct Manager, Commander, Evidence, Response, human approval, approval-ledger confirmation, and Audit messages;
2. a correlation table proving the same `tr_s01` and `rp_tr_s01` across those artifacts;
3. a redacted ApprovalRecord and canonical approval ledger projection with timestamp, actor category, event type, plan reference, previous/terminal hashes, and a successful integrity verification result;
4. independent proof that the user-controlled human session produced the approval action, without exposing account or Matrix identifiers;
5. explicit evidence that the ResponsePlan remained `pending_approval` and no real action was executed.

If these historical artifacts cannot be recovered, any new live run requires fresh preflight and explicit user authorization; this QA does not authorize it.

## Minimum remaining blockers for V-05

Even after a future V-08 PASS, V-05 remains blocked until at least:

- the independently reviewable live four-role/Matrix/human-approval evidence package above exists;
- S-09/Codex Security establishes no untriaged high-severity finding and repository secret hygiene is closed for release;
- Higress/model-gateway governance evidence is captured without credentials;
- current runtime/team membership and final demo evidence are reconciled with the repository documentation;
- R-08AX is either completed and independently verified or explicitly excluded from the release baseline without making unsupported restart-persistence claims.

## Conclusion

V-08B is **FAIL**. R-08B's code-security deficiencies from the old V-08 are fixed and reproducible, and WorkBuddy's account is plausible and internally consistent. The available repository evidence still requires trusting WorkBuddy's narration for the crucial same-trace, role-separated, user-approved, hash-valid live chain. That is insufficient to independently overturn the old V-08 FAIL or release V-05.
