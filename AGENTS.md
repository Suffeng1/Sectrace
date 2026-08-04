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
