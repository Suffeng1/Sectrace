# R-09BB live MCP approval-tool attestation

- Date: 2026-08-11
- Result: `PASS`
- Data boundary: synthetic S01 only; no real action
- Trace / plan: `tr_s01_s09live` / `rp_tr_s01_s09live`
- Matrix sends / retries: 1 / 0
- MCP mutations: intake 1, evidence 1, response 1, approval 1, Audit 0

## Controlled live flow

The current runtime preflight returned `READY_RUNTIME`. Commander created one
fresh distinct synthetic trace, completed Evidence, and created one high-risk
ResponsePlan at `pending_approval`. No Audit call was made.

In the Commander room, the exact structured approval JSON was sent by clicking
the uniquely identified Element composer control
`.mx_MessageComposer_actions .mx_MessageComposer_sendMessage[role="button"]`
once. The composer became empty and exactly one matching timeline event appeared:

`$pelrTVPkMqU1GVO751qIj5wBEFLmKRt7FEVvL3tJmgo`

The event body bound `trace_id=tr_s01_s09live`,
`plan_ref=rp_tr_s01_s09live`, `decision=approved`, and the synthetic-only
reason. Earlier R-09B8/R-09B9/R-09BA keyboard and wrong-room attempts produced
zero Matrix messages; they are retained as separate stopped records and were
not counted as retries of this successful send.

Commander then invoked `sectrace.ledger.log_approval` exactly once. The caller
supplied only trace, plan, decision, and Matrix event ID. The live verifier
server-fetched the Matrix event and established the human facts. The result was:

- approver role / ledger actor: `human_operator`
- approval status / event type: `approved` / `approval.approved`
- approval timestamp: `2026-08-11T15:29:04.065000Z`
- event: `ledger_004`
- previous hash: `cb663b40a2241513f4052a475bc2a83003de232f5410eb735741b118484a751b`
- terminal hash: `838180dace6cb7c708a6b698a75e944d7d91a569f03644d054762a45bfa5e8ac`
- event digest: `5f32d06262c93bfd770f29c38b988fe25fdc2812b82a0a14caf5d2a689c1c880`
- reason digest: `52b994000e5c46542a554ea4241758065066ef3f0ef90fde42c65278ab5083e8`

## Independent local state projection

`data/mcp-state/tr_s01_s09live.json` was loaded through `SafeMCPAdapter` and
the canonical ledger verifier. The projection confirmed:

- schema-valid S01 synthetic scenario with `real_data=false`;
- exact event order `incident.created -> evidence.completed ->
  response.pending_approval -> approval.approved`;
- exactly four ledger records and one `human_operator` approval;
- valid chained hashes and the same terminal hash returned by the live tool;
- event-ID and reason SHA-256 values exactly present in the approval payload;
- Response remains `pending_approval`, Approval is `approved`, and Audit is
  absent.

The retained `pending_approval` Response is intentional: approval records the
human decision but does not execute any action. No screenshot was copied into
the repository because it contained a logged-in private Matrix page; the
structured event ID, persisted canonical state, and hash-bound tool result are
the durable evidence.

## Gate conclusion

The live MCP approval tool no longer trusts caller-supplied approver or reason
facts. A fresh admin-origin Matrix event was fetched and bound to the current
trace and plan, and a Commander-owned single call produced the canonical human
approval event without invoking Audit or any real action. R-09BB closes the
remaining S-09 live MCP-tool attestation gate.
