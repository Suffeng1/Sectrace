import asyncio

from httpx import ASGITransport, AsyncClient

from src.app.main import create_app


def test_demo_page_and_api_show_pending_human_approval() -> None:
    async def probe() -> tuple:
        async with AsyncClient(
            transport=ASGITransport(app=create_app()), base_url="http://test"
        ) as client:
            return await client.get("/"), await client.post("/api/demo/S01")

    page, replay = asyncio.run(probe())

    assert page.status_code == 200
    assert "SecTrace" in page.text
    assert "待人工审批" in page.text
    assert replay.status_code == 200
    payload = replay.json()
    assert payload["trace_id"] == "tr_s01"
    assert payload["response_plan"]["status"] == "pending_approval"
    assert payload["approval"]["status"] == "pending"