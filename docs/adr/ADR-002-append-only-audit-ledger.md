# ADR-002: Append-only canonical JSON audit ledger

**Date**: 2026-08-04  
**Status**: accepted  
**Deciders**: 00 主控与集成

## Context

The audit report must be replayable and must distinguish validated history from generated narrative. The MVP needs a local mechanism with no cloud dependency that reveals tampering and preserves Agent handoffs.

## Decision

Use append-only JSONL records with the fields `event_id`, `trace_id`, `at`, `actor`, `event_type`, `payload_ref`, `prev_hash`, and `hash`. Canonical JSON is UTF-8, sorted keys, compact `,`/`:` separators, and no insignificant whitespace. For each record, serialize the object without `hash`; calculate `SHA-256(prev_hash + canonical_json_bytes)` and store its lowercase hex digest as `hash`. The genesis `prev_hash` is empty; every later record repeats the prior record hash.

Replay reads records in file order, validates their contracts, recomputes each hash, and requires each `prev_hash` to equal the preceding hash. Only then may it deterministically project an `AuditBundle`; ordering, inputs, and projection rules are fixed, so the same validated ledger yields the same structured result.

Payloads are references, not unbounded raw secrets. Before persistence and report projection, redact credential-like values and secret tokens as `[REDACTED]`; retain safe identifiers such as `trace_id` and synthetic event references. A missing or redacted value remains explicitly missing and is never reconstructed.

## Alternatives considered

### Mutable database rows without a ledger

- **Pros**: easy queries and updates.
- **Cons**: handoff history and tampering are less inspectable.
- **Why not**: replay integrity is a core evaluation criterion.

### Blockchain or external event store

- **Pros**: stronger distributed guarantees.
- **Cons**: unnecessary services, cost, and deployment risk for a synthetic local demo.
- **Why not**: JSONL plus chained SHA-256 meets the MVP's deterministic audit requirement.

## Consequences

Consumers obtain inspectable, deterministic history and explicit integrity failures. The ledger must not be edited in place; corrections are new events. The local hash chain is tamper-evident, not a replacement for a production signing or key-management system.
