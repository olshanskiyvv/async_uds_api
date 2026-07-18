import traceback

import aiofiles
import httpx
import pytest
import respx
from httpx import Response

from async_uds_api import (
    UDSClient,
    UDSImageDownloadError,
    UDSImageReadError,
    UDSImageUnsupportedSourceError,
    UDSImageUploadError,
)
from tests.fixtures.images import IMAGE_UPLOAD_URL_RESPONSE
from tests.test_client import FakeLogger

IMAGE_UPLOAD_URL_POST_RESPONSE = {
    **IMAGE_UPLOAD_URL_RESPONSE,
    "method": "POST",
}


def formatted_traceback(exc: BaseException) -> str:
    """Render the exception exactly as logging.exception would."""
    return "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )


class TestImagesAPI:
    async def test_get_upload_url_success(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        result = await uds_client.images.get_upload_url("image/jpeg")

        assert result.image_id is not None
        assert result.url is not None
        assert result.method == "PUT"

    async def test_get_upload_url_validates_mime_type(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError):
            await uds_client.images.get_upload_url("invalid-mime-type")

    def test_validate_content_type_valid(self, uds_client):
        uds_client.images._validate_content_type("image/jpeg")
        uds_client.images._validate_content_type("image/png")
        uds_client.images._validate_content_type("image/webp")
        uds_client.images._validate_content_type("application/pdf")

    def test_validate_content_type_invalid(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError):
            uds_client.images._validate_content_type("invalid")

        with pytest.raises(UDSImageUnsupportedSourceError):
            uds_client.images._validate_content_type("not-a-mime")

    def test_detect_content_type_from_jpg(self, uds_client):
        result = uds_client.images._detect_content_type("/path/to/image.jpg")

        assert result == "image/jpeg"

    def test_detect_content_type_from_png(self, uds_client):
        result = uds_client.images._detect_content_type("/path/to/image.png")

        assert result == "image/png"

    def test_detect_content_type_unknown_raises(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError):
            uds_client.images._detect_content_type("/path/to/file.unknown")

    async def test_upload_from_bytes_requires_content_type(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            await uds_client.images.upload(b"image data")

        assert "content_type is required" in str(exc_info.value)

    async def test_upload_from_file_not_found(self, uds_client):
        with pytest.raises(UDSImageReadError) as exc_info:
            await uds_client.images.upload("/nonexistent/file.jpg")

        assert "File not found" in str(exc_info.value)

    async def test_upload_from_file_success(self, uds_client, tmp_path):
        test_file = tmp_path / "test_image.jpg"
        test_content = b"fake image data"

        async with aiofiles.open(test_file, "wb") as f:
            await f.write(test_content)

        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        result = await uds_client.images.upload(str(test_file))

        assert result == IMAGE_UPLOAD_URL_RESPONSE["imageId"]

    async def test_upload_from_url_success(self, uds_client):
        respx.get("https://example.com/image.jpg").mock(
            return_value=Response(200, content=b"fake image data")
        )
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        result = await uds_client.images.upload(
            "https://example.com/image.jpg"
        )

        assert result == IMAGE_UPLOAD_URL_RESPONSE["imageId"]

    async def test_upload_from_url_failure(self, uds_client):
        respx.get("https://example.com/notfound.jpg").mock(
            return_value=Response(404)
        )

        with pytest.raises(UDSImageDownloadError):
            await uds_client.images.upload("https://example.com/notfound.jpg")

    async def test_upload_from_bytes_success(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        result = await uds_client.images.upload(
            b"fake image data", "image/jpeg"
        )

        assert result == IMAGE_UPLOAD_URL_RESPONSE["imageId"]

    async def test_upload_via_post_method(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_POST_RESPONSE)
        )
        respx.post(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        result = await uds_client.images.upload(
            b"fake image data", "image/jpeg"
        )

        assert result == IMAGE_UPLOAD_URL_POST_RESPONSE["imageId"]

    async def test_upload_unsupported_method_raises(self, uds_client):
        bad_response = {**IMAGE_UPLOAD_URL_RESPONSE, "method": "PATCH"}
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=bad_response)
        )

        with pytest.raises(
            UDSImageUploadError, match="Unsupported upload method"
        ):
            await uds_client.images.upload(b"fake image data", "image/jpeg")

    async def test_upload_to_presigned_url_error(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(500))

        with pytest.raises(UDSImageUploadError):
            await uds_client.images.upload(b"image", "image/jpeg")

    async def test_download_failure_does_not_leak_signature(
        self, mock_httpx, caplog
    ):
        import logging

        signed_url = (
            "https://example.com/notfound.jpg"
            "?X-Amz-Signature=super-secret-signature"
        )
        respx.get(signed_url).mock(return_value=Response(404))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageDownloadError) as exc_info:
                    await client.images._download_from_url(signed_url)

        assert "super-secret-signature" not in caplog.text
        assert "super-secret-signature" not in str(exc_info.value)
        assert "super-secret-signature" not in formatted_traceback(
            exc_info.value
        )

    async def test_custom_logger_receives_image_events(self, mock_httpx):
        fake = FakeLogger()
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            logger=fake,
        ) as client:
            await client.images.get_upload_url("image/png")

        events = [event for _, event, _ in fake.events]
        assert "uds.image.upload_url_received" in events


class TestImageUrlContainment:
    async def test_download_failure_with_host_case_mismatch(
        self, mock_httpx, caplog
    ):
        import logging

        signed_url = (
            "https://EXAMPLE.com/notfound.jpg?X-Amz-Signature=DEADBEEFSECRET"
        )
        respx.get(signed_url).mock(return_value=Response(404))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageDownloadError) as exc_info:
                    await client.images._download_from_url(signed_url)

        assert "DEADBEEFSECRET" not in caplog.text
        assert "DEADBEEFSECRET" not in str(exc_info.value)
        assert "DEADBEEFSECRET" not in formatted_traceback(exc_info.value)
        assert exc_info.value.__cause__ is not None

    async def test_upload_failure_does_not_leak_signature(
        self, mock_httpx, caplog
    ):
        import logging

        signed_url = (
            "https://storage.googleapis.com/test-bucket/test-image"
            "?X-Amz-Signature=DEADBEEFSECRET"
        )
        upload_response = {**IMAGE_UPLOAD_URL_RESPONSE, "url": signed_url}
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=upload_response)
        )
        respx.put(signed_url).mock(return_value=Response(403))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageUploadError) as exc_info:
                    await client.images.upload(b"image", "image/jpeg")

        assert "DEADBEEFSECRET" not in caplog.text
        assert "DEADBEEFSECRET" not in str(exc_info.value)
        assert "DEADBEEFSECRET" not in formatted_traceback(exc_info.value)
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, httpx.HTTPStatusError)
        assert exc_info.value.__cause__.response.status_code == 403

    async def test_transport_error_does_not_leak_signature(
        self, mock_httpx, caplog
    ):
        import logging

        signed_url = (
            "https://cdn.example.com/pic.jpg?X-Amz-Signature=DEADBEEFSECRET"
        )
        respx.route(
            method="GET", host="cdn.example.com", path="/pic.jpg"
        ).mock(
            side_effect=httpx.ConnectError(
                f"failed to connect to {signed_url}"
            )
        )

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageDownloadError) as exc_info:
                    await client.images._download_from_url(signed_url)

        assert "DEADBEEFSECRET" not in caplog.text
        assert "DEADBEEFSECRET" not in str(exc_info.value)
        assert "DEADBEEFSECRET" not in formatted_traceback(exc_info.value)
        assert isinstance(exc_info.value.__cause__, httpx.ConnectError)

    async def test_upload_start_log_masks_source_url(self, mock_httpx, caplog):
        import logging

        signed_url = (
            "https://cdn.example.com/pic.jpg?X-Amz-Signature=DEADBEEFSECRET"
        )
        respx.get(signed_url).mock(
            return_value=Response(200, content=b"image")
        )
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                await client.images.upload(signed_url)

        assert "DEADBEEFSECRET" not in caplog.text
        for record in caplog.records:
            assert "DEADBEEFSECRET" not in str(getattr(record, "uds", ""))
        assert "https://cdn.example.com/pic.jpg?***" in caplog.text

    async def test_upload_start_log_keeps_local_path_intact(
        self, mock_httpx, caplog, tmp_path
    ):
        import logging

        path = tmp_path / "what?ever.jpg"
        path.write_bytes(b"image")
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )
        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                await client.images.upload(str(path))

        assert str(path) in caplog.text

    def test_detect_content_type_masks_url_query(self, uds_client):
        signed_url = (
            "https://cdn.example.com/pic?X-Amz-Signature=DEADBEEFSECRET"
        )

        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            uds_client.images._detect_content_type(signed_url)

        assert "DEADBEEFSECRET" not in str(exc_info.value)
        assert "https://cdn.example.com/pic?***" in str(exc_info.value)

    def test_detect_content_type_keeps_local_path_intact(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            uds_client.images._detect_content_type("./rel/what?ever.zzz")

        assert "./rel/what?ever.zzz" in str(exc_info.value)
