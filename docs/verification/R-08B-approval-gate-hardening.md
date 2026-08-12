# R-08B Approval Gate Hardening

- Ticket: R-08B
- Date: 2026-08-08
- Result: `CODE_COMPLETE_RUNTIME_INCOMPLETE`
- Data boundary: synthetic/de-identified data only

## Security fixes

- `plan_ref` must equal the current trace's `response_plan.plan_id`.
- The only accepted approver and ledger actor is `human_operator`.
- Approval `reason` is represented in the ledger only by a SHA-256 reference; raw free text is not returned or placed in the audit report.
- Approval transitions are one-way from `pending` to `approved` or `rejected`.
- Repeated decisions and approved/rejected overrides are rejected before mutation.
- Failed calls preserve both ApprovalRecord and the full ledger byte-for-byte at the model/dict level.
- Approved and rejected paths have independent tests.

## Contract reconciliation

- Four production Worker YAML files and their resource test agree on `deepseek-chat`.
- The independent smoke Worker remains on its CRD-compatibility model and was not changed.
- MCP source binding is restored to `127.0.0.1`; the live process has not been restarted, so container reachability is pending runtime authorization.
- README, MCP docstrings, Demo evidence index/script, and the current tool-policy note now describe six tools.
- Historical V-05 and V-08 verification conclusions were not changed.

## Tests

- TDD red state: 7 expected failures exposed the missing boundaries.
- R-08B approval failure-boundary tests: 7 passed.
- Focused approval, binding, and production-resource tests: 20 passed.
- Complete pytest with an isolated project-local temporary directory: 47 passed.
- `git diff --check`: passed.

## Runtime evidence

- Live six-tool schema: pending.
- Loopback-bound container reachability: pending.
- New single S01 trace: not sent.
- Same-trace four-role chain: not collected.
- User-performed approval/rejection: not performed.
- Final Audit result: pending.

`NEEDS-AUTHORIZATION`: restart/update MCP, perform any necessary Manager synchronization or restart, and dispatch exactly one new synthetic S01. The user must perform the approval or rejection personally after reviewing the visible trace and plan.

## Rollback

Before runtime propagation, rollback is limited to a targeted reverse patch of the R-08B changes in the adapter, tests, binding constant, and directly affected documentation. Because the worktree contains unrelated uncommitted changes, do not use reset, checkout, or broad file replacement. After runtime propagation, restart the MCP service with the previously reviewed source only after explicit authorization.

No commit or push was performed.
## Phase 2 bounded observation

- MCP source/runtime update: completed; host initialize returned HTTP 200.
- MCP listen address: `127.0.0.1` only.
- Commander via `host.docker.internal`: HTTP 200 initialize.
- Audit via `host.docker.internal`: HTTP 200 initialize.
- Live schema: Commander and Audit each reported exactly six tools, including `sectrace.ledger.log_approval`.
- New synthetic S01 send attempts: exactly 1; Matrix accepted it with HTTP 200.
- Bounded observation window: 10 minutes, read-only.
- Commander/Evidence/Response/Audit stage messages observed: none.
- `pending_approval` reached: no.
- User approval/rejection: not requested at a visible trace because the trace stages did not appear.
- No second S01, approval message, real response, or remediation action was sent.

Phase 2 remains incomplete and is not ready for independent V-08 re-execution.
## R-08D corrected Manager mention dispatch

- Two preliminary scripts stopped at read-only prechecks; Matrix send attempts from them: 0.
- The confirmed ingress topology was one Manager consumer and one Commander in the visible Commander DM.
- Final prechecks passed: ingress topology, Manager mention role, fixed synthetic S01 content, and no credential/room identifier/real data in the message body.
- Corrected R-08D Matrix send attempts: exactly 1; accepted with HTTP 200.
- Read-only observation window: 10 minutes.
- Manager consumption observed: no.
- Commander, Evidence, Response, Audit stage messages observed: none.
- Same-trace continuity: unavailable.
- `pending_approval`: not reached.
- User approval/rejection: not performed; no plan reference was produced for review.
- No retry, restart, configuration change, resource apply/delete, real action, commit, or push occurred.

R-08D stopped as required and remains incomplete.