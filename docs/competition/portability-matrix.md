# SecTrace industry portability matrix

Status: `DESIGN_HYPOTHESIS_NO_EXTERNAL_DEPLOYMENT_CLAIM`

SecTrace's reuse boundary is a governance pattern: typed handoffs, a human gate,
an append-only ledger and an independent Audit. Reuse is not zero-configuration
deployment. Each target domain needs mapped synthetic/de-identified test cases,
adapter review and independent acceptance before any external claim.

## Invariant core versus Replaceable adapter layer

| Concern | Invariant core | Replaceable adapter layer | Migration acceptance gate |
| --- | --- | --- | --- |
| Workflow Contract | Preserve versioned Incident → Evidence → ResponsePlan → Approval → Audit semantics, same-trace binding and fail-closed validation. | Map domain input/output fields and vocabulary into the existing semantic roles; change role prompts and presentation labels. | Contract/schema tests prove required fields, trace continuity and backward compatibility. A Contract-shape change requires a versioned migration decision. |
| Human gate | Preserve advice-only behavior, explicit pending state, one bound human decision and refusal of invalid or duplicate decisions. | Replace the approval identity/event source and its verifier, allowlist and policy mapping. | Synthetic positive/negative identity and trace/plan binding tests pass; no caller self-attestation. |
| Ledger | Preserve canonical serialization, append-only ordering, hash linkage, terminal hash and rejection of tampered state. | Replace storage/transport integration and retention configuration without changing canonical event meaning silently. | Golden-chain, tamper, restart and ordering tests pass on the target adapter. |
| Independent Audit | Preserve separation from proposal generation, required-artifact checks, missing-requirement reporting and integrity validation. | Replace domain-specific Audit rules, report vocabulary and evidence-reference renderer. | Known-good, missing, conflicting and tampered synthetic cases produce the declared terminal conditions. |
| Evidence ingestion | Preserve source references, fact/inference/unknown separation and trace binding. | Replace log, ticket, document or transaction data-source adapters and normalization rules. | Provenance, redaction, size/time and malformed-input tests pass; external access is least privilege and separately authorized. |
| Role behavior | Preserve responsibility separation and typed handoff boundaries. | Replace domain prompts, taxonomies, escalation wording and role labels while retaining ownership boundaries. | Prompt/resource contract tests show permissions and outputs match the target domain policy. |
| Gateway and orchestration | Preserve route-only management and least-capability tool assignment. | Replace Agent gateway, model gateway, messaging transport and deployment configuration. | Route/capability tests and a fresh environment-specific preflight pass. Historical evidence is not reused. |
| Safety and privacy | Preserve synthetic/de-identified testing, secret exclusion, advice-only output and explicit human authority. | Replace organization-specific data classification, retention, redaction and operator policy. | Privacy/security review documents allowed data and proves no secret or prohibited content enters reports or ledgers. |

## Target-domain mapping

| Target scenario | Incident/intake adaptation | Evidence adaptation | Advice pending human gate | Audit adaptation | What is not yet proved |
| --- | --- | --- | --- | --- | --- |
| Security incident governance | Synthetic alert/case source and severity taxonomy | Log/ticket source adapters and provenance rules | Containment/remediation advice reviewed by an allowed operator | Security control, approval and ledger completeness | No current environment or production outcome is asserted. |
| Compliance exception review | Policy-exception request and control identifiers | Policy text, attestations and exception history | Accept/mitigate/escalate recommendation reviewed by a control owner | Required evidence, expiry, approval and segregation-of-duty checks | No regulator acceptance or enterprise rollout is asserted. |
| Fraud case triage | De-identified transaction/case signals | Transaction features and investigator notes with provenance | Hold/review/escalate advice reviewed by an authorized analyst | Decision binding, evidence lineage and review completeness | No fraud-detection accuracy or financial benefit is asserted. |
| Operations change governance | Synthetic change request, service and risk classification | Test, dependency and rollback evidence | Proceed/defer advice reviewed by a change authority | Change evidence, decision, rollback coverage and ledger integrity | No deployment automation, availability gain or external integration is asserted. |

## Migration sequence

1. Select one target scenario and define its allowed synthetic/de-identified data.
2. Map domain fields to the existing Contract semantics and record any gap.
3. Implement only the required data-source, prompt, approval-source and gateway
   adapters; do not weaken the gate, ledger or Audit separation.
4. Freeze deterministic positive, invalid-state, missing, conflicting and
   tampered cases.
5. Run Contract, binding, ledger, privacy and Audit tests, followed by independent
   QA in the target environment.
6. Describe only the verified scope. External effectiveness and operational
   benefits remain unknown until measured under an approved protocol.
