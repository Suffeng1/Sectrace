# R-08BC Manager Route-Only Restoration

- Date: 2026-08-11
- Result: `BOUNDARY_RESTORED_QA_PENDING`
- Authorized mutation: remove only `mcpServers.sectrace` from Manager `config/mcporter.json`
- Restart count: 0

## Preconditions

The user explicitly authorized R-08BC. A fresh read-only runtime preflight returned `READY_RUNTIME` before mutation.

The minimized before projection identified one exact Manager workspace configuration target:

```json
{
  "path_class": "manager_workspace_config",
  "root_key": "mcpServers",
  "server_names": ["sectrace"],
  "has_sectrace": true,
  "file_sha256": "3ddb11cc883e05c648e9ff9407a6d0082156e8d5e5c9b3db2cdcefc13f51b6df",
  "rest_sha256": "691f62624936af38f0e6b2ac6c8b43162a23696696f62d5037d9eb2b43bd73c5"
}
```

No endpoint, credential, value, or complete configuration was emitted.

## Surgical mutation

One JSON-aware atomic mutation was executed inside the Manager container:

- asserted that `mcpServers.sectrace` existed;
- computed the semantic hash of the complete configuration after removing only that key;
- removed that key once;
- verified the resulting object had the same semantic hash;
- wrote one unique temporary file, flushed it with `fsync`, and renamed it atomically;
- preserved file mode;
- left no temporary residue.

Mutation result:

```json
{
  "mutation_count": 1,
  "removed_key": "mcpServers.sectrace",
  "other_semantics_unchanged": true,
  "remaining_server_names": [],
  "temporary_residue": false
}
```

## Postconditions

The after projection showed:

- `server_names=[]`
- `has_sectrace=false`
- file SHA-256 `d8e397af03b5b032f21d0aa967086f0c78b33c87b76f2e9898ae0a144df7de02`
- semantic SHA-256 `691f62624936af38f0e6b2ac6c8b43162a23696696f62d5037d9eb2b43bd73c5`, exactly matching the before `rest_sha256`
- temporary residue count 0

A single read-only Manager capability probe failed before transport with exit 1 and `Unknown MCP server 'sectrace'`. Commander independently listed exactly six live SecTrace tools, including `sectrace.ledger.log_approval`, over the configured `host.docker.internal` endpoint. A fresh write-after runtime preflight returned `READY_RUNTIME`, including Host and Commander TCP/initialize checks.

## Preserved evidence and boundary

The governance-invalid approved `tr_s01` state and its five-event append-only ledger were not changed, cleared, rewritten, or reused. No service was restarted; no S01, Matrix message, approval, Audit call, file sync, smoke action, commit, or push occurred. This restoration does not retroactively validate R-08BB or pass V-08. A clean replacement requires a distinct synthetic trace/run and separate authorizations.
