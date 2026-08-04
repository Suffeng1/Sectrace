"""Lightweight local SecTrace demo application."""

from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from src.app.orchestrator import run_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
S01_PATH = REPO_ROOT / "data" / "scenarios" / "S01.json"

DEMO_HTML = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>SecTrace</title>
<style>body{font-family:system-ui;background:#0b1020;color:#e8edf8;max-width:960px;margin:40px auto;padding:0 20px}button{background:#52d3a5;border:0;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#151d33;padding:18px;border-radius:8px}.gate{color:#ffd166}</style></head>
<body><h1>SecTrace 安全事件多 Agent 协同审计</h1>
<p>固定合成场景 S01：Commander → Evidence → Response → Audit</p>
<p class="gate">高风险计划：待人工审批；本演示不会执行任何真实动作。</p>
<button onclick="runDemo()">重放 S01</button><pre id="result">点击按钮生成可审计链。</pre>
<script>async function runDemo(){const r=await fetch('/api/demo/S01',{method:'POST'});document.getElementById('result').textContent=JSON.stringify(await r.json(),null,2)}</script>
</body></html>"""


async def home(request) -> HTMLResponse:
    return HTMLResponse(DEMO_HTML)


async def replay_s01(request) -> JSONResponse:
    result = run_demo(S01_PATH)
    return JSONResponse(result)


def create_app() -> Starlette:
    return Starlette(
        debug=False,
        routes=[Route("/", home), Route("/api/demo/S01", replay_s01, methods=["POST"])],
    )


app = create_app()
