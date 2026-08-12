# Handoff: R-07 (v3 — CR model override is the real blocker)

- 角色：00 主控与运行时集成
- Ticket：R-07 S01 dispatch unblocking
- 状态：**NEEDS-AUTHORIZATION**
- 日期：2026-08-08
- 数据边界：仅合成/脱敏数据；无真实处置、无人工审批点击

> **v3 修正**：v2 认为只要 `AGENTTEAMS_LLM_API_KEY=` 并重建容器即可。Codex 执行后发现 Manager 运行时仍显示旧模型。WorkBuddy 进一步诊断发现：**Manager CR `spec.model` 和 Worker CR `spec.model` 会覆盖容器 env，这才是当前真正的卡点**。LLM 连通性本身已经恢复。

## Authorization scope

The user has authorized WorkBuddy to perform read-only diagnosis only. All file modifications, container operations, service restarts, CR patches, and S01 dispatch must be performed by Codex in the 00 dialog after explicit user authorization.

## WorkBuddy findings (read-only, source-code verified)

### 1. LLM connectivity is already working

Tested from `agentteams-manager` container:

```bash
curl -s -X POST http://agentteams-controller:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <redacted-credential>" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hello"}],"max_tokens":10}'
```

Response: valid chat completion, `model: deepseek-v4-flash`, content present.
Same test passed via `http://aigw-local.agentteams.io:8080/v1` and `http://host.docker.internal:18080/v1`.

Conclusion:
- Higress `default-ai-route` is correctly routing to `deepseekv4flash` provider.
- Manager Gateway key auth is working.
- AI Gateway URL `http://agentteams-controller:8080/v1` is reachable from Manager and Workers.

### 2. The real blocker: CR `spec.model` overrides env

#### Manager CR

Queried embedded k8s API in Controller:

```bash
curl -s -k --header "Authorization: Bearer <redacted-credential>" \
  https://127.0.0.1:6443/apis/agentteams.io/v1beta1/namespaces/default/managers/default
```

Result:

```json
{
  "spec": {
    "config": {},
    "image": "higress-registry.cn-hangzhou.cr.aliyuncs.com/agentteams/agentteams-manager:latest",
    "model": "GLM-4.7",
    "runtime": "openclaw"
  }
}
```

Source-code verification:

| File | Line(s) | Finding |
|------|---------|---------|
| `agentteams-controller/internal/service/worker_env.go` | 65-67 | `if spec.Model != "" { env["AGENTTEAMS_DEFAULT_MODEL"] = spec.Model }` — Manager CR `spec.model` overrides controller env |
| `agentteams-controller/internal/controller/manager_reconcile_container.go` | 162-166 | `managerEnv := r.EnvBuilder.BuildManager(...)` then `mergeUserEnv(managerEnv, m.Spec.Env, ...)` — CR env wins |
| `agentteams-controller/internal/config/config.go` | 808 | Controller's `ManagerAgentEnv()` also passes `AGENTTEAMS_DEFAULT_MODEL`, but BuildManager overrides it with CR spec |

Therefore, even though `agentteams-manager.env` has `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat` and Controller's process env shows `deepseek-chat`, the Manager container env ends up with `GLM-4.7` because the Manager CR `spec.model` is `GLM-4.7`.

#### Worker CRs

Queried `sectrace-commander` Worker CR:

```json
{
  "spec": {
    "model": "qwen3.6-plus",
    "runtime": "openclaw"
  }
}
```

Verified in container: `/root/agentteams-fs/agents/sectrace-commander/openclaw.json` has `"primary": "agentteams-gateway/qwen3.6-plus"`.

All four Worker YAMLs currently specify `model: qwen3.6-plus` (example: `hiclaw/sectrace-agents/sectrace-commander.yaml` line 6).

### 3. Impact

- **Functionally**, calls still route through Higress to `deepseek-v4-flash` because Higress `default-ai-route` ignores/rewrites the requested model. Codex observed runs completing.
- **Semantically**, the system is configured to tell OpenClaw "primary model is GLM-4.7 / qwen3.6-plus", which is inconsistent with the user's intent to use DeepSeek.
- For project traceability (官号接手、初赛评审), the CRs and YAMLs must declare `deepseek-chat` as the model.

### 4. `agentteams-manager.env` current state (already correct)

```ini
AGENTTEAMS_LLM_PROVIDER=deepseekv4flash
AGENTTEAMS_DEFAULT_MODEL=deepseek-chat
AGENTTEAMS_LLM_API_KEY=
AGENTTEAMS_OPENAI_BASE_URL=https://api.deepseek.com/v1
```

No change needed to this file.

### 5. MCP server state

`src/app/mcp_server.py` has `BIND_HOST = "0.0.0.0"`. Verify it is running on port 19090 before S01; restart if not.

### 6. Worker SOUL.md state

All four SOUL.md were updated by Codex previously and persist in MinIO. They should survive Worker recreation.

## Tasks for Codex (00 dialog)

### Task 1: Patch Manager CR `spec.model`

Run inside `agentteams-controller` container (or from host via `docker exec`):

```bash
TOKEN="<redacted-credential>"
APISERVER="https://127.0.0.1:6443"

docker exec agentteams-controller sh -c "
  curl -s -k -X PATCH \\
    --header \"Authorization: Bearer ${TOKEN}\" \\
    --header \"Content-Type: application/merge-patch+json\" \\
    --data '{\"spec\":{\"model\":\"deepseek-chat\"}}' \\
    ${APISERVER}/apis/agentteams.io/v1beta1/namespaces/default/managers/default
"
```

Expected result: HTTP 200 and response JSON shows `"model": "deepseek-chat"`.

This will cause the controller to detect a spec hash drift and **recreate** the Manager container. The new Manager container will have `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat` and will regenerate `/root/manager-workspace/openclaw.json` with `"primary": "agentteams-gateway/deepseek-chat"`.

### Task 2: Update Worker YAML model fields

Edit these four files in the project directory:

- `hiclaw/sectrace-agents/sectrace-commander.yaml`
- `hiclaw/sectrace-agents/sectrace-evidence.yaml`
- `hiclaw/sectrace-agents/sectrace-response.yaml`
- `hiclaw/sectrace-agents/sectrace-audit.yaml`

In each file, change:

```yaml
spec:
  model: qwen3.6-plus
```

To:

```yaml
spec:
  model: deepseek-chat
```

### Task 3: Re-apply Worker YAMLs to update Worker CRs

After Manager is recreated and healthy (wait for `docker ps` to show `agentteams-manager` running and port 18888 responding):

```bash
cd "<repo-root>"

# Option A: if agentteams-apply.sh exists
# ./hiclaw/install/agentteams-apply.sh hiclaw/sectrace-agents/sectrace-commander.yaml
# ./hiclaw/install/agentteams-apply.sh hiclaw/sectrace-agents/sectrace-evidence.yaml
# ./hiclaw/install/agentteams-apply.sh hiclaw/sectrace-agents/sectrace-response.yaml
# ./hiclaw/install/agentteams-apply.sh hiclaw/sectrace-agents/sectrace-audit.yaml

# Option B: direct CR apply via embedded k8s API (use the same token as Task 1)
TOKEN="<redacted-credential>"
APISERVER="https://127.0.0.1:6443"
for f in hiclaw/sectrace-agents/sectrace-{commander,evidence,response,audit}.yaml; do
  docker exec -i agentteams-controller sh -c "
    curl -s -k -X PUT \\
      --header \"Authorization: Bearer ${TOKEN}\" \\
      --header \"Content-Type: application/yaml\" \\
      --data-binary @- \\
      ${APISERVER}/apis/agentteams.io/v1beta1/namespaces/default/workers/$(basename $f .yaml)
  " < "$f"
done
```

Re-applying the YAMLs updates the Worker CRs. The controller will detect spec hash drift and recreate each Worker container with `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat`, regenerating their `openclaw.json`.

### Task 4: Verify model propagation

```bash
# Manager CR
docker exec agentteams-controller sh -c '
  curl -s -k --header "Authorization: Bearer <redacted-credential>" \
    https://127.0.0.1:6443/apis/agentteams.io/v1beta1/namespaces/default/managers/default | \
    grep -o "\"model\": \"[^\"]*\""
'

# Manager container env
docker exec agentteams-manager env | grep AGENTTEAMS_DEFAULT_MODEL

# Manager openclaw.json primary model
docker exec agentteams-manager cat /root/manager-workspace/openclaw.json | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['agents']['defaults']['model']['primary'])"

# Worker CRs (should all show deepseek-chat)
docker exec agentteams-controller sh -c '
  for w in sectrace-commander sectrace-evidence sectrace-response sectrace-audit; do
    echo -n "$w: "
    curl -s -k --header "Authorization: Bearer <redacted-credential>" \
      https://127.0.0.1:6443/apis/agentteams.io/v1beta1/namespaces/default/workers/$w | \
      grep -o "\"model\": \"[^\"]*\""
  done
'

# Worker openclaw.json primary models (after recreation)
for w in sectrace-commander sectrace-evidence sectrace-response sectrace-audit; do
  echo -n "$w: "
  docker exec agentteams-worker-$w cat /root/agentteams-fs/agents/$w/openclaw.json 2>/dev/null | \
    python3 -c "import json,sys; print(json.load(sys.stdin)['agents']['defaults']['model']['primary'])" 2>/dev/null || echo "not ready"
done
```

Expected:
- Manager CR model: `deepseek-chat`
- Manager env: `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat`
- Manager openclaw.json primary: `agentteams-gateway/deepseek-chat`
- All Worker CRs model: `deepseek-chat`
- All Worker openclaw.json primary: `agentteams-gateway/deepseek-chat`

### Task 5: Verify LLM connectivity from a Worker

```bash
docker exec agentteams-worker-sectrace-commander curl -s -X POST http://agentteams-controller:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hello"}],"max_tokens":10}'
```

Expected: valid JSON, `model: deepseek-v4-flash`, content present.

### Task 6: Verify MCP server

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:19090/mcp -X POST \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

If not 200, start it persistently:

```bash
cd "<repo-root>"
nohup <python-command> src/app/mcp_server.py > mcp_server.log 2>&1 &
```

### Task 7: Re-send S01 and observe the chain

Once Tasks 1-6 pass:

```bash
TXN="s01-$(date +%s)"
curl -s -X PUT "http://localhost:18080/_matrix/client/v3/rooms/<matrix-room-or-event-id>/send/m.room.message/${TXN}" \
  -H "Authorization: Bearer <redacted-credential>" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"m.text","body":"@sectrace-commander 请处理安全演练场景 S01。执行 mcporter call --server sectrace --tool sectrace.intake.create_incident scenario_id=S01，创建 IncidentCase，确认 trace_id，然后将收集证据任务交给 sectrace-evidence。"}'
```

Then observe:
1. Commander room messages (`/_matrix/client/v3/rooms/.../messages`).
2. Commander container logs for LLM activity and mcporter calls.
3. Evidence / response / audit rooms/logs for downstream handoffs.
4. Whether the chain reaches `pending_approval`.

### Task 8: Record results

Update `docs/verification/R-07-s01-dispatch.md` and create `docs/handoffs/H-R08.md` if human approval is reached.

## Current snapshot (2026-08-08 12:55)

- `agentteams-manager.env`: correct (`AGENTTEAMS_LLM_PROVIDER=deepseekv4flash`, `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat`, `AGENTTEAMS_LLM_API_KEY=` empty).
- Controller container env: `AGENTTEAMS_DEFAULT_MODEL=deepseek-chat`.
- **Manager CR `spec.model`: `GLM-4.7` (stale)** — this overrides Controller env and sets Manager container env to `GLM-4.7`.
- **Worker CRs `spec.model`: `qwen3.6-plus` (stale)** — same override mechanism.
- Higress: user manually configured `deepseekv4flash` provider → `api.deepseek.com`; `default-ai-route` uses it. LLM calls return valid DeepSeek responses.
- MCP server: verify running before S01.
- Worker SOUL.md: updated previously, persists in MinIO.
- Docker containers: Controller, Manager, 5 Workers all running.
- S01: not yet sent in this turn.

## Blockers

1. **Manager CR `spec.model` must be patched to `deepseek-chat`**; this triggers Controller to recreate the Manager container with the correct env and openclaw.json.
2. **Worker YAMLs must change `model: qwen3.6-plus` → `model: deepseek-chat`** and be re-applied so Worker CRs update and Workers recreate.
3. Codex must be authorized to patch CRs, modify project YAMLs, and recreate Manager/Worker containers.
