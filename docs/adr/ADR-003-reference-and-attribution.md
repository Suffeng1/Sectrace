# ADR-003: Conceptual reference and attribution boundary

**Date**: 2026-08-04  
**Status**: accepted  
**Deciders**: 00 主控与集成

## Context

SecTrace takes inspiration from public work on security-agent workflows, append-only stores, and specification-led delivery. It must be clear that the MVP's documentation and code are independently written.

## Decision

The following are conceptual-only references; **no source copied**.

- [AiSOC](https://github.com/GoogleCloudPlatform/ai-security-ops) informs the ideas of auditable security automation, provenance, and gated decisions.
- [ESAA-Security](https://github.com/ESAA-Security/ESAA) informs the ideas of structured boundaries and replay-oriented security workflows.
- [sample-specship](https://github.com/github/spec-kit) informs the specification → contract → test → verification workflow pattern.

The links are cited for ideas, not as dependencies, vendored source, or evidence of runtime behavior. SecTrace implements its models, ledger algorithm, documentation, and tests from scratch.

## Alternatives considered

### Copy or adapt source implementation

- **Pros**: faster initial implementation.
- **Cons**: unclear licensing/provenance and a weaker contest artefact.
- **Why not**: explicit independent implementation and auditable attribution are required.

### Omit references

- **Pros**: shorter documentation.
- **Cons**: hides design influences.
- **Why not**: transparent conceptual attribution helps reviewers evaluate the architecture.

## Consequences

Future contributors may consult the cited public material for concepts, but must maintain this no-copy boundary and record any new dependency or source attribution explicitly.
