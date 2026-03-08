import pytest
import respx
from httpx import Response

from async_uds_api.models import TagsPage
from tests.fixtures.api_responses import TAGS_LIST_RESPONSE


@pytest.mark.asyncio
class TestTagsAPI:
    async def test_list_tags_success(self, uds_client):
        """Test successful tags list retrieval."""
        respx.get("https://api.uds.app/partner/v2/tags").mock(
            return_value=Response(200, json=TAGS_LIST_RESPONSE)
        )

        result = await uds_client.tags.list()

        assert isinstance(result, TagsPage)
        assert result.total == 2
        assert len(result.rows) == 2
        assert result.rows[0].name == "VIP"

    async def test_list_tags_empty(self, uds_client):
        """Test empty tags list."""
        respx.get("https://api.uds.app/partner/v2/tags").mock(
            return_value=Response(200, json={"rows": [], "total": 0})
        )

        result = await uds_client.tags.list()

        assert isinstance(result, TagsPage)
        assert result.total == 0
        assert len(result.rows) == 0
