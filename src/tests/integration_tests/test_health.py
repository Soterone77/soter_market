import pytest


@pytest.mark.asyncio
async def test_healthcheck(ac):
    response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
