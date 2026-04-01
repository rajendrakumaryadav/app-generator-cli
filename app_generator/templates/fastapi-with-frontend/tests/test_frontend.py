"""Tests for the rendered frontend homepage."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_homepage_renders(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.text
    assert "Generated with AppGenerator" in response.text

