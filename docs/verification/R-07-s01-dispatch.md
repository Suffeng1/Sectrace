# R-07 S01 Dispatch

- Ticket: R-07
- Date: 2026-08-08
- Data boundary: synthetic/de-identified S01 only
- Result: PENDING_APPROVAL_REACHED_WITH_INCOMPLETE_ROLE_EVIDENCE

## Authorization and safety

The user authorized the Manager and Worker CR updates, four Worker YAML edits, container recreation, one S01 resend, and observation through `pending_approval`.

- S01 send limit: one attempt, no automatic retry
- Human approval click: not performed
- Real response action: not performed
- Real enterprise systems: not accessed
- Credentials, tokens, room identifiers, message bodies, and raw logs: not recorded

## Task results

1. Manager CR patch returned HTTP 200 and set `spec.model` to `deepseek-chat`.
2. Controller recreated Manager. The container is running; its model environment setting is `deepseek-chat`, and OpenClaw primary is `agentteams-gateway/deepseek-chat`.
3. The four project Worker YAML files now declare `model: deepseek-chat`.
4. The first Commander full-YAML PUT was rejected with HTTP 422 because update metadata lacked `resourceVersion`; no CR change occurred. The four YAMLs were then applied with their current server-side versions in memory. All four updates returned HTTP 200 and triggered recreation.
5. All four Worker CRs report `deepseek-chat` and `Running`. All four OpenClaw primary values are `agentteams-gateway/deepseek-chat`. Worker containers expose no model environment variable; model propagation is carried by the generated OpenClaw configuration.
6. An unauthenticated Higress probe returned HTTP 401 as expected for the protected route. The in-memory authenticated probe returned HTTP 200, valid JSON, upstream model `deepseek-v4-flash`, and non-empty content.
7. The MCP initialize probe on port 19090 returned HTTP 200 with an initialize result.
8. S01 was sent exactly once and accepted with HTTP 200. No resend or retry occurred.

## Chain observation

- Commander activity observed: yes
- Evidence activity observed in the dispatch window: no
- Response activity observed in the dispatch window: no
- Audit activity observed in the dispatch window: no
- `pending_approval` observed: yes
- Observation stopped immediately at `pending_approval`: yes

The approval state appeared in the Element Web room named `Worker: sectrace-commander`. Because no independent Evidence, Response, or Audit messages were observed before the stop gate, R-07 does not prove the complete Commander -> Evidence -> Response -> Audit chain. Human review should confirm those stage artifacts before approval.

## Approval boundary

Approval entry: Element Web, `Worker: sectrace-commander`.

Codex did not click an approval control and did not execute any real remediation.