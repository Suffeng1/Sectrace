# HiClaw runtime inventory (redacted)

This inventory is documentation-only. It was derived from the approved SecTrace V2 plan without reading user-owned HiClaw configuration.

| Service role | Local address | Purpose |
| --- | --- | --- |
| HiClaw Manager | `localhost:18888` | Coordinates Worker tasks |
| Matrix / Element Web | `localhost:18088` | Displays task and handoff records |
| Higress gateway | `localhost:18080` | Proxies governed model traffic |

## Excluded data

The inventory intentionally records no usernames, passwords, tokens, account names, model-provider URL, model-provider identity, or credential-bearing configuration.

## Verification boundary

Service health, versions, schemas, and any additional localhost ports are not asserted in R-00. They belong to H-01 and must be discovered without printing credentials.
