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


class TestImageSourceLogging:
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

    async def test_upload_start_log_keeps_source_url_intact(
        self, mock_httpx, caplog
    ):
        import logging

        source_url = "https://cdn.example.com/pic.jpg?token=abc123"
        respx.get(source_url).mock(
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
                await client.images.upload(source_url)

        assert (
            f"Uploading from {source_url} with content_type=image/jpeg"
            in caplog.text
        )

    def test_detect_content_type_keeps_local_path_intact(self, uds_client):
        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            uds_client.images._detect_content_type("./rel/what?ever.zzz")

        assert "./rel/what?ever.zzz" in str(exc_info.value)

    def test_detect_content_type_keeps_url_intact(self, uds_client):
        url = "https://cdn.example.com/pic?token=abc123"

        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            uds_client.images._detect_content_type(url)

        assert str(exc_info.value) == (
            f"Cannot detect content type for '{url}'. "
            "Provide content_type explicitly."
        )


class TestImageMessageWording:
    async def test_download_failed_message_matches_original(
        self, mock_httpx, caplog
    ):
        import logging

        url = "https://cdn.example.com/notfound.jpg?token=abc123"
        respx.get(url).mock(return_value=Response(404))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageDownloadError) as exc_info:
                    await client.images._download_from_url(url)

        cause = exc_info.value.__cause__
        expected = f"Failed to download image from {url}: {cause}"
        assert str(exc_info.value) == expected
        assert expected in caplog.text
        assert f"Downloading image from URL: {url}" in caplog.text

    async def test_upload_failed_message_matches_original(
        self, mock_httpx, caplog
    ):
        import logging

        signed_url = (
            "https://storage.googleapis.com/test-bucket/test-image?sig=abc123"
        )
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(
                200, json={**IMAGE_UPLOAD_URL_RESPONSE, "url": signed_url}
            )
        )
        respx.put(signed_url).mock(return_value=Response(403))

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageUploadError) as exc_info:
                    await client.images.upload(b"image", "image/jpeg")

        cause = exc_info.value.__cause__
        expected = f"Failed to upload image: {cause}"
        assert str(exc_info.value) == expected
        assert expected in caplog.text
        assert isinstance(cause, httpx.HTTPStatusError)

    async def test_file_read_failed_message_matches_original(
        self, mock_httpx, caplog, tmp_path, monkeypatch
    ):
        import logging

        path = tmp_path / "pic.png"
        path.write_bytes(b"image")
        boom = OSError("disk on fire")

        def explode(*args, **kwargs):
            raise boom

        monkeypatch.setattr(aiofiles, "open", explode)

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(UDSImageReadError) as exc_info:
                    await client.images._read_from_file(path)

        expected = f"Failed to read file {path}: {boom}"
        assert str(exc_info.value) == expected
        assert expected in caplog.text

    async def test_download_traceback_keeps_httpx_text(
        self, mock_httpx, caplog
    ):
        url = "https://cdn.example.com/notfound.jpg"
        respx.get(url).mock(return_value=Response(404))

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(UDSImageDownloadError) as exc_info:
                await client.images._download_from_url(url)

        cause = exc_info.value.__cause__
        assert isinstance(cause, httpx.HTTPStatusError)
        assert url in str(cause)
        assert url in formatted_traceback(exc_info.value)


class TestNonHttpSource:
    async def test_windows_path_is_treated_as_filesystem_path(
        self, uds_client
    ):
        with pytest.raises(UDSImageReadError) as exc_info:
            await uds_client.images._read_image_data("C:\\images\\pic.png")

        assert "File not found" in str(exc_info.value)

    async def test_colon_bearing_relative_path_is_a_filesystem_path(
        self, uds_client
    ):
        with pytest.raises(UDSImageReadError) as exc_info:
            await uds_client.images._read_image_data("backup:photos/a.png")

        assert "File not found" in str(exc_info.value)

    async def test_non_http_scheme_is_treated_as_filesystem_path(
        self, uds_client
    ):
        with pytest.raises(UDSImageReadError) as exc_info:
            await uds_client.images._read_image_data("ftp://host/key.png")

        assert "File not found" in str(exc_info.value)

    async def test_posix_paths_are_treated_as_filesystem_paths(
        self, uds_client, tmp_path
    ):
        target = tmp_path / "pic.png"
        target.write_bytes(b"image")

        data = await uds_client.images._read_image_data(str(target))
        assert data == b"image"

        with pytest.raises(UDSImageReadError):
            await uds_client.images._read_image_data("relative/pic.png")
