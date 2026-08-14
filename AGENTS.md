# SecTrace collaboration rules

## Ownership

- **00** owns repository root, configuration, shared app/UI, specifications, contracts, Tickets, ADRs, status, and Git.
- **01** owns Commander, intake, matching tests, and H-T01.
- **02** owns Evidence, matching tests, and H-T02.
- **03** owns Response, matching tests, and H-T03.
- **04** owns Audit, matching tests, and H-T04.
- **05** writes only `docs/verification/` and never business code.
- Shared-contract issues go only in a Handoff for 00 to resolve.

## Safety boundaries

- Use synthetic or de-identified data only.
- Do not attack, scan, connect to real systems, or take security action.
- Treat high-risk output as advice only and require a human gate.
- Do not invent evidence; preserve `trace_id` across every handoff.
- Never include secrets in reports.

## Mandatory resume preflight

- At the start of every **new conversation**, after a **computer reboot**, and after any meaningful runtime change, choose the **lowest necessary mode** and run `scripts/sectrace-preflight.ps1` before work begins.
- Use `code` for repository-only work, `runtime` for Docker/AgentTeams/MCP work, and `live` before any Matrix or S01 activity. Historical PASS evidence never replaces the current preflight.
- Every **runtime mutation** still requires separate, explicit user authorization. The preflight **must not be used as a launcher** or treated as permission to start, stop, restart, apply, delete, send, retry, approve, commit, or push.
- Follow `docs/runtime/reboot-preflight.md`; stop at the first blocked category and never touch `sectrace-smoke` as part of resume checks.

## Controller notification protocol

- Every delegated Codex task must receive the controller task's `thread_id` and
  `host_id` in its initial prompt. The controller must not rely on polling alone.
- Before a delegated task ends a turn with any terminal or attention-required
  state, it must use the Codex task messaging tool to send a structured status
  message to the controller. This applies to `COMPLETE`, `BLOCKED`,
  `AUTH_REQUIRED`, `QA_PASS`, and `QA_FAIL`.
- The message must include: task ID, status, tests/result, files changed, blocker
  or next handoff, and whether commit/push/runtime/live activity occurred.
- Send the controller message before the delegated task's final answer. A final
  answer in the delegated task is not a substitute for this notification.
- If the messaging tool is unavailable or the send fails, the delegated task
  must state `CONTROLLER_NOTIFY_FAILED` in its final answer. The controller must
  then use `wait_threads` before starting dependent work.
- The controller records each created task and actively waits for its status.
  Receiving a notification does not waive independent QA or any authorization
  gate.
