"""Unit tests for Jellyfin client authentication."""

import httpx
import pytest

from jfc.clients.jellyfin import JellyfinClient


def test_uses_authorization_header_not_legacy_token() -> None:
    """Jellyfin 12 rejects X-Emby-Token; the client must use the Authorization scheme."""
    client = JellyfinClient(url="http://jellyfin:8096", api_key="abc123")

    assert client.headers["Authorization"] == 'MediaBrowser Token="abc123"'
    assert "X-Emby-Token" not in client.headers


@pytest.mark.asyncio
async def test_authorization_header_sent_on_requests() -> None:
    """The header must actually reach the server on normal API calls."""
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.headers)
        return httpx.Response(200, json=[])

    client = JellyfinClient(url="http://jellyfin:8096", api_key="abc123")
    client._client = httpx.AsyncClient(
        base_url=client.base_url,
        headers=client.headers,
        transport=httpx.MockTransport(handler),
    )

    assert await client.get_libraries() == []
    assert seen["authorization"] == 'MediaBrowser Token="abc123"'
    assert "x-emby-token" not in seen
    await client.close()
