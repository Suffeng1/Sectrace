#!/usr/bin/env python3
"""Start HiClaw/AgentTeams containers directly, bypassing the install script."""
import subprocess
import sys
import os
import time
import json

HOME = os.path.expanduser("~")
ENV_FILE = os.path.join(HOME, "agentteams-manager.env")
REGISTRY = "higress-registry.cn-hangzhou.cr.aliyuncs.com"
EMBEDDED_IMAGE = f"{REGISTRY}/agentteams/agentteams-embedded:latest"

def load_env(path):
    env = {}
    with open(path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                # Strip inline comments
                if ' #' in value:
                    value = value.split(' #')[0].strip()
                env[key] = value
    return env

def run(cmd, check=True, capture=True):
    print(f"  > {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, capture_output=capture, text=True, shell=False)
    if capture and result.stdout:
        print(result.stdout[:2000])
    if capture and result.stderr:
        print(f"  STDERR: {result.stderr[:1000]}", file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

def docker_ps():
    result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"],
                          capture_output=True, text=True)
    return result.stdout

def main():
    print("=== HiClaw/AgentTeams Direct Startup ===\n")

    # Load env file
    if not os.path.exists(ENV_FILE):
        print(f"ERROR: env file not found at {ENV_FILE}")
        sys.exit(1)
    env = load_env(ENV_FILE)
    print(f"Loaded {len(env)} config entries from {ENV_FILE}")

    # Check Docker is running
    result = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: Docker is not running. Start Docker Desktop first.")
        sys.exit(1)
    print("Docker is running.")

    # Step 1: Create network
    print("\n--- Step 1: Create Docker network ---")
    subprocess.run(["docker", "network", "create", "agentteams-net"],
                   capture_output=True, text=True)
    # Ignore error if network already exists
    print("Network agentteams-net ready.")

    # Step 2: Remove old containers
    print("\n--- Step 2: Remove old containers ---")
    for name in ["agentteams-manager", "agentteams-controller", "agentteams-docker-proxy"]:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)
    print("Old containers removed.")

    # Step 3: Start embedded controller
    print("\n--- Step 3: Start agentteams-controller (embedded) ---")
    print(f"Image: {EMBEDDED_IMAGE}")

    # Build env args
    ctrl_envs = [
        "-e", f"AGENTTEAMS_ADMIN_USER={env.get('AGENTTEAMS_ADMIN_USER', 'admin')}",
        "-e", f"AGENTTEAMS_ADMIN_PASSWORD={env.get('AGENTTEAMS_ADMIN_PASSWORD', '')}",
        "-e", f"AGENTTEAMS_MANAGER_PASSWORD={env.get('AGENTTEAMS_MANAGER_PASSWORD', '')}",
        "-e", f"AGENTTEAMS_REGISTRATION_TOKEN={env.get('AGENTTEAMS_REGISTRATION_TOKEN', '')}",
        "-e", f"AGENTTEAMS_MINIO_USER={env.get('AGENTTEAMS_MINIO_USER', '')}",
        "-e", f"AGENTTEAMS_MINIO_PASSWORD={env.get('AGENTTEAMS_MINIO_PASSWORD', '')}",
        "-e", f"AGENTTEAMS_LLM_PROVIDER={env.get('AGENTTEAMS_LLM_PROVIDER', 'openai-compat')}",
        "-e", f"AGENTTEAMS_LLM_API_KEY={env.get('AGENTTEAMS_LLM_API_KEY', '')}",
        "-e", f"AGENTTEAMS_DEFAULT_MODEL={env.get('AGENTTEAMS_DEFAULT_MODEL', '')}",
        "-e", f"AGENTTEAMS_MANAGER_GATEWAY_KEY={env.get('AGENTTEAMS_MANAGER_GATEWAY_KEY', '')}",
        "-e", f"AGENTTEAMS_MANAGER_RUNTIME={env.get('AGENTTEAMS_MANAGER_RUNTIME', 'openclaw')}",
        "-e", f"AGENTTEAMS_DEFAULT_WORKER_RUNTIME={env.get('AGENTTEAMS_DEFAULT_WORKER_RUNTIME', 'openclaw')}",
        "-e", f"AGENTTEAMS_MATRIX_DOMAIN={env.get('AGENTTEAMS_MATRIX_DOMAIN', '')}",
        "-e", f"AGENTTEAMS_MATRIX_E2EE={env.get('AGENTTEAMS_MATRIX_E2EE', '0')}",
        "-e", "AGENTTEAMS_ELEMENT_HOMESERVER_URL=http://127.0.0.1:18080",
        "-e", "AGENTTEAMS_MATRIX_URL=http://127.0.0.1:6167",
        "-e", "AGENTTEAMS_MINIO_ENDPOINT=http://127.0.0.1:9000",
        "-e", "AGENTTEAMS_MINIO_BUCKET=agentteams-storage",
        "-e", "AGENTTEAMS_FS_ENDPOINT=http://127.0.0.1:9000",
        "-e", f"AGENTTEAMS_AI_GATEWAY_URL=http://aigw-local.agentteams.io:8080",
        "-e", "AGENTTEAMS_CONTROLLER_URL=http://agentteams-controller:8090",
        "-e", "AGENTTEAMS_DOCKER_NETWORK=agentteams-net",
        "-e", f"AGENTTEAMS_WORKSPACE_DIR={env.get('AGENTTEAMS_WORKSPACE_DIR', '')}",
        "-e", f"AGENTTEAMS_HOST_SHARE_DIR={env.get('AGENTTEAMS_HOST_SHARE_DIR', '')}",
        "-e", "AGENTTEAMS_MANAGER_ENABLED=true",
        "-e", f"AGENTTEAMS_PORT_MANAGER_CONSOLE={env.get('AGENTTEAMS_PORT_MANAGER_CONSOLE', '18888')}",
        "-e", f"AGENTTEAMS_WORKER_IMAGE={env.get('AGENTTEAMS_WORKER_IMAGE', '')}",
        "-e", f"AGENTTEAMS_MANAGER_IMAGE={env.get('AGENTTEAMS_MANAGER_IMAGE', 'higress-registry.cn-hangzhou.cr.aliyuncs.com/agentteams/agentteams-manager:latest')}",
        "-e", f"AGENTTEAMS_MANAGER_COPAW_IMAGE={env.get('AGENTTEAMS_MANAGER_COPAW_IMAGE', 'higress-registry.cn-hangzhou.cr.aliyuncs.com/agentteams/agentteams-manager-copaw:latest')}",
        "-e", f"AGENTTEAMS_COPAW_WORKER_IMAGE={env.get('AGENTTEAMS_COPAW_WORKER_IMAGE', '')}",
        "-e", f"AGENTTEAMS_HERMES_WORKER_IMAGE={env.get('AGENTTEAMS_HERMES_WORKER_IMAGE', '')}",
        "-e", f"AGENTTEAMS_OPENAI_BASE_URL={env.get('AGENTTEAMS_OPENAI_BASE_URL', '')}",
        "-e", f"AGENTTEAMS_MODEL_CONTEXT_WINDOW={env.get('AGENTTEAMS_MODEL_CONTEXT_WINDOW', '')}",
        "-e", f"AGENTTEAMS_MODEL_MAX_TOKENS={env.get('AGENTTEAMS_MODEL_MAX_TOKENS', '')}",
        "-e", f"AGENTTEAMS_MODEL_REASONING={env.get('AGENTTEAMS_MODEL_REASONING', '')}",
        "-e", f"AGENTTEAMS_MODEL_VISION={env.get('AGENTTEAMS_MODEL_VISION', '')}",
        "-e", f"AGENTTEAMS_LANGUAGE={env.get('AGENTTEAMS_LANGUAGE', 'zh')}",
        "-e", "AGENTTEAMS_CMS_TRACES_ENABLED=false",
        "-e", f"AGENTTEAMS_CMS_SERVICE_NAME={env.get('AGENTTEAMS_CMS_SERVICE_NAME', 'agentteams-manager')}",
        "-e", "AGENTTEAMS_CMS_METRICS_ENABLED=false",
        "-e", "TZ=Asia/Shanghai",
    ]

    # Add appservice tokens
    ctrl_envs += ["-e", "AGENTTEAMS_MATRIX_APPSERVICE_ENABLED=true"]
    if env.get('AGENTTEAMS_MATRIX_APPSERVICE_AS_TOKEN'):
        ctrl_envs += ["-e", f"AGENTTEAMS_MATRIX_APPSERVICE_AS_TOKEN={env['AGENTTEAMS_MATRIX_APPSERVICE_AS_TOKEN']}"]
    if env.get('AGENTTEAMS_MATRIX_APPSERVICE_HS_TOKEN'):
        ctrl_envs += ["-e", f"AGENTTEAMS_MATRIX_APPSERVICE_HS_TOKEN={env['AGENTTEAMS_MATRIX_APPSERVICE_HS_TOKEN']}"]

    docker_run_cmd = [
        "docker", "run", "-d",
        "--name", "agentteams-controller",
        "--network", "agentteams-net",
        "--network-alias", "matrix-local.agentteams.io",
        "--network-alias", "aigw-local.agentteams.io",
        "--network-alias", "fs-local.agentteams.io",
    ] + ctrl_envs + [
        "-v", "//var/run/docker.sock:/var/run/docker.sock",
        "--security-opt", "label=disable",
        "-v", "agentteams-data:/data",
        "-v", f"{env.get('AGENTTEAMS_WORKSPACE_DIR', '')}:/root/agentteams-fs/agents/manager",
        "-p", f"{env.get('AGENTTEAMS_PORT_GATEWAY', '18080')}:8080",
        "-p", f"{env.get('AGENTTEAMS_PORT_CONSOLE', '18001')}:8001",
        "-p", f"{env.get('AGENTTEAMS_PORT_ELEMENT_WEB', '18088')}:8088",
        # Note: Manager Console port (18888) is NOT mapped here - it's used by the Manager container
        # The controller only needs to know the port number via env var to pass it to the Manager
        "--restart", "unless-stopped",
        EMBEDDED_IMAGE
    ]

    result = subprocess.run(docker_run_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Failed to start controller container:")
        print(f"  stdout: {result.stdout}")
        print(f"  stderr: {result.stderr}")
        sys.exit(1)
    print(f"Controller container started: {result.stdout.strip()[:12]}...")

    # Step 4: Wait for Tuwunel (Matrix)
    print("\n--- Step 4: Waiting for Tuwunel (Matrix) ---")
    max_wait = 180
    elapsed = 0
    while elapsed < max_wait:
        result = subprocess.run(
            ["docker", "exec", "agentteams-controller",
             "curl", "-sf", "http://127.0.0.1:6167/_tuwunel/server_version"],
            capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Tuwunel (Matrix) is ready! ({elapsed}s) Response: {result.stdout.strip()}")
            break
        time.sleep(3)
        elapsed += 3
        if elapsed % 15 == 0:
            print(f"  Still waiting... ({elapsed}s)")
    else:
        print(f"ERROR: Tuwunel (Matrix) not ready after {max_wait}s")
        print("Container logs (last 20 lines):")
        logs = subprocess.run(["docker", "logs", "--tail", "20", "agentteams-controller"],
                            capture_output=True, text=True)
        print(logs.stdout[-1000:] if logs.stdout else "(no stdout)")
        print(logs.stderr[-1000:] if logs.stderr else "(no stderr)")
        sys.exit(1)

    # Step 5: Wait for MinIO
    print("\n--- Step 5: Waiting for MinIO ---")
    elapsed = 0
    while elapsed < 60:
        result = subprocess.run(
            ["docker", "exec", "agentteams-controller",
             "curl", "-sf", "http://127.0.0.1:9000/minio/health/live"],
            capture_output=True, text=True)
        if result.returncode == 0:
            print(f"MinIO is ready! ({elapsed}s)")
            break
        time.sleep(2)
        elapsed += 2
    else:
        print(f"WARNING: MinIO not ready after 60s (continuing anyway)")

    # Step 6: Wait for Higress Gateway
    print("\n--- Step 6: Waiting for Higress Gateway ---")
    elapsed = 0
    while elapsed < 120:
        result = subprocess.run(
            ["docker", "exec", "agentteams-controller",
             "curl", "-sf", "http://127.0.0.1:8080/status"],
            capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Higress Gateway is ready! ({elapsed}s)")
            break
        time.sleep(3)
        elapsed += 3
        if elapsed % 15 == 0:
            print(f"  Still waiting... ({elapsed}s)")
    else:
        print(f"WARNING: Higress Gateway not ready after 120s (continuing anyway)")

    # Step 7: Wait for Manager Agent container
    print("\n--- Step 7: Waiting for Manager Agent container ---")
    max_wait = 300
    elapsed = 0
    while elapsed < max_wait:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True)
        if "agentteams-manager" in result.stdout:
            print(f"Manager Agent container detected! ({elapsed}s)")
            break
        time.sleep(3)
        elapsed += 3
        if elapsed % 30 == 0:
            print(f"  Still waiting... ({elapsed}s)")
    else:
        print(f"ERROR: Manager Agent container not created after {max_wait}s")
        print("Controller logs (last 30 lines):")
        logs = subprocess.run(
            ["docker", "exec", "agentteams-controller",
             "tail", "-30", "/var/log/agentteams/agentteams-controller-error.log"],
            capture_output=True, text=True)
        print(logs.stdout if logs.stdout else "(no logs)")
        sys.exit(1)

    # Step 8: Wait for Manager to be running
    print("\n--- Step 8: Waiting for Manager Agent to be running ---")
    elapsed = 0
    while elapsed < 120:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", "agentteams-manager"],
            capture_output=True, text=True)
        status = result.stdout.strip()
        if status == "running":
            print(f"Manager Agent is running! ({elapsed}s)")
            break
        elif status == "exited":
            print(f"ERROR: Manager Agent exited unexpectedly")
            logs = subprocess.run(["docker", "logs", "--tail", "20", "agentteams-manager"],
                                capture_output=True, text=True)
            print(logs.stdout[-500:] if logs.stdout else "")
            print(logs.stderr[-500:] if logs.stderr else "")
            sys.exit(1)
        time.sleep(3)
        elapsed += 3

    # Final status
    print("\n=== Installation Complete ===")
    print("\nContainer status:")
    result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
                          capture_output=True, text=True)
    print(result.stdout)

    gateway_port = env.get('AGENTTEAMS_PORT_GATEWAY', '18080')
    console_port = env.get('AGENTTEAMS_PORT_CONSOLE', '18001')
    element_port = env.get('AGENTTEAMS_PORT_ELEMENT_WEB', '18088')
    mgr_console_port = env.get('AGENTTEAMS_PORT_MANAGER_CONSOLE', '18888')

    print(f"\nAccess points:")
    print(f"  Higress Gateway:  http://localhost:{gateway_port}")
    print(f"  Higress Console:  http://localhost:{console_port}")
    print(f"  Element Web:      http://localhost:{element_port}")
    print(f"  Manager Console:  http://localhost:{mgr_console_port}")
    print(f"\n  Admin user:     {env.get('AGENTTEAMS_ADMIN_USER', 'admin')}")
    print(f"  Admin password: {env.get('AGENTTEAMS_ADMIN_PASSWORD', '(see env file)')}")

if __name__ == "__main__":
    main()
