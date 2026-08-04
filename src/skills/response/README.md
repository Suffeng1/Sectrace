# Response planning skill

This skill converts supplied `EvidenceItem` records into an advice-only
`ResponsePlan`. Strong, high-confidence facts produce a high-risk plan that is
always `pending_approval` and includes rollback guidance. Unknown or
insufficient evidence produces a low-risk draft that explicitly says the event
cannot be confirmed.

The skill has no execution, network, shell, account, data-deletion, or
permission-change capability. Every action is phrased as a recommendation.
