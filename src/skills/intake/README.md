# Intake normalization

Commander passes a scenario payload to `normalize_scenario` before creating an
`IncidentCase`. The intake boundary accepts synthetic or de-identified exercise
data only and rejects a payload whose `real_data` marker is `true`.

Accepted events retain their scenario-local `event_ref` values. Intake does not
draw conclusions, connect to systems, scan targets, or perform remediation.
