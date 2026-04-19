import respx
from httpx import Response

from async_uds_api.models import (
    CreateOperation,
    CreateOperationReceipt,
    ImageUploadUrl,
    Operation,
    OperationsPage,
)
from tests.fixtures.images import IMAGE_UPLOAD_URL_RESPONSE
from tests.fixtures.operations import (
    OPERATION_RESPONSE,
    OPERATIONS_LIST_RESPONSE,
)


class TestOperationsAPI:
    async def test_list_operations_success(self, uds_client):
        """Test successful operations list retrieval."""
        respx.get("https://api.uds.app/partner/v2/operations").mock(
            return_value=Response(200, json=OPERATIONS_LIST_RESPONSE)
        )

        result = await uds_client.operations.list()

        assert isinstance(result, OperationsPage)
        assert result.total == 1
        assert len(result.rows) == 1

    async def test_list_operations_with_pagination(self, uds_client):
        """Test operations list with pagination."""
        respx.get(
            "https://api.uds.app/partner/v2/operations",
            params={"max": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=OPERATIONS_LIST_RESPONSE))

        result = await uds_client.operations.list(max=10, offset=0)

        assert isinstance(result, OperationsPage)

    async def test_get_operation_success(self, uds_client):
        """Test successful operation retrieval by ID."""
        operation_id = 123

        respx.get(
            f"https://api.uds.app/partner/v2/operations/{operation_id}"
        ).mock(return_value=Response(200, json=OPERATION_RESPONSE))

        result = await uds_client.operations.get(operation_id)

        assert isinstance(result, Operation)
        assert result.id == 123

    async def test_create_operation_success(self, uds_client):
        """Test successful operation creation."""
        operation = CreateOperation(
            receipt=CreateOperationReceipt(total=100.0, cash=50.0, points=50.0)
        )

        respx.post("https://api.uds.app/partner/v2/operations").mock(
            return_value=Response(200, json=OPERATION_RESPONSE)
        )

        result = await uds_client.operations.create(operation)

        assert isinstance(result, Operation)

    async def test_refund_operation_full(self, uds_client):
        """Test full operation refund."""
        operation_id = 123

        respx.post(
            f"https://api.uds.app/partner/v2/operations/{operation_id}/refund"
        ).mock(return_value=Response(200, json=OPERATION_RESPONSE))

        result = await uds_client.operations.refund(operation_id)

        assert isinstance(result, Operation)

    async def test_iter_all_operations_single_page(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/operations",
            params={"max": "50"},
        ).mock(return_value=Response(200, json=OPERATIONS_LIST_RESPONSE))

        result = [o async for o in uds_client.operations.iter_all()]

        assert len(result) == 1
        assert isinstance(result[0], Operation)

    async def test_iter_all_operations_multiple_pages(self, uds_client):
        row = OPERATIONS_LIST_RESPONSE["rows"][0]
        page1 = {"rows": [row], "cursor": "cursor1", "total": 2}
        page2 = {"rows": [row], "total": 2}
        responses = [Response(200, json=page1), Response(200, json=page2)]

        def handler(request):  # type: ignore[no-untyped-def]
            return responses.pop(0)

        respx.get("https://api.uds.app/partner/v2/operations").mock(
            side_effect=handler
        )

        result = [o async for o in uds_client.operations.iter_all(page_size=1)]

        assert len(result) == 2

    async def test_iter_all_operations_empty(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/operations",
            params={"max": "50"},
        ).mock(return_value=Response(200, json={"rows": []}))

        result = [o async for o in uds_client.operations.iter_all()]

        assert result == []

    async def test_get_upload_url_success(self, uds_client):
        """Test successful presigned URL retrieval for images."""
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        result = await uds_client.images.get_upload_url("image/jpeg")

        assert isinstance(result, ImageUploadUrl)
        assert result.image_id is not None
        assert result.url is not None
        assert result.method == "PUT"
