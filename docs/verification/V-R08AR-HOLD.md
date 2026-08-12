# R-08AR Independent QA Hold

- Date: 2026-08-09
- Result: **INCOMPLETE — HOLD PENDING FIX AND RE-VERIFICATION**
- Supersedes: `docs/verification/V-R08AR-independent-qa.md`

## Withdrawal of release approval

R-08AR must not be released or treated as QA PASS. Subsequent controller review identified two gate-design issues that require correction and fresh independent QA:

1. local Python demo UI port 19080 is treated as a universal hard prerequisite for `runtime`; this violates the lowest-necessary-mode principle and can incorrectly block otherwise valid Controller/Manager/MCP read-only work;
2. `host_mcp_process_present` mirrors listener presence and cannot serve as independent process-presence evidence.

## Required correction before re-verification

- Make the local demo UI optional and non-blocking for general runtime preflight.
- Add read-only Controller, Higress, and Manager core-port gates in the correct dependency order.
- Remove or correct the listener-as-process category.
- Update focused tests, runbook, AGENTS/README references if affected, and R-08AR evidence.
- Re-run independent 05 QA after the controller publishes the corrected evidence.

## Boundary

No business code or runtime change was made by QA. No service was started or restarted, and no message, approval, resource operation, smoke operation, commit, or push occurred.

## Conclusion

R-08AR is **INCOMPLETE**. The earlier independent PASS is withdrawn and must not authorize runtime or live work. Wait for the controller's corrected implementation and evidence before re-verification.
