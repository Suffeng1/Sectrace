# Evidence correlation skill

`analyze_case(incident, scenario)` evaluates only the supplied synthetic or
de-identified scenario events. It returns a list of contract v1.0
`EvidenceItem` values and a deterministic risk path.

Rules:

- Every item preserves the input `IncidentCase.trace_id`.
- Every conclusion is classified as `fact`, `inference`, or `unknown` and has
  a supplied `source_ref`.
- The S01 sequence is correlated only when anomalous login, privilege
  elevation, and bulk data access are all supplied in order.
- Incomplete evidence returns `unknown`, `insufficient`, low confidence, and
  the explicit text `无法确认`.
- `real_data: true` is rejected. The skill has no connector, network access,
  scanning, or remediation capability.
