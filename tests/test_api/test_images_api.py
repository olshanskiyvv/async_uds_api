import pytest
import respx
from httpx import Response

from async_uds_api import (
    UDSImageReadError,
    UDSImageUnsupportedSourceError,
    UDSImageUploadError,
)
from tests.fixtures.api_responses import IMAGE_UPLOAD_URL_RESPONSE


class TestImagesAPI:
    async def test_get_upload_url_success(self, uds_client):
        """Test successful presigned URL retrieval."""
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        result = await uds_client.images.get_upload_url("image/jpeg")

        assert result.image_id is not None
        assert result.url is not None
        assert result.method == "PUT"

    async def test_get_upload_url_validates_mime_type(self, uds_client):
        """Test that get_upload_url validates MIME type."""
        with pytest.raises(UDSImageUnsupportedSourceError):
            await uds_client.images.get_upload_url("invalid-mime-type")

    def test_validate_content_type_valid(self, uds_client):
        """Test valid MIME types validation."""
        uds_client.images._validate_content_type("image/jpeg")
        uds_client.images._validate_content_type("image/png")
        uds_client.images._validate_content_type("image/webp")
        uds_client.images._validate_content_type("application/pdf")

    def test_validate_content_type_invalid(self, uds_client):
        """Test invalid MIME types validation."""
        with pytest.raises(UDSImageUnsupportedSourceError):
            uds_client.images._validate_content_type("invalid")

        with pytest.raises(UDSImageUnsupportedSourceError):
            uds_client.images._validate_content_type("not-a-mime")

    def test_detect_content_type_from_jpg(self, uds_client):
        """Test content type detection from .jpg file."""
        result = uds_client.images._detect_content_type("/path/to/image.jpg")

        assert result == "image/jpeg"

    def test_detect_content_type_from_png(self, uds_client):
        """Test content type detection from .png file."""
        result = uds_client.images._detect_content_type("/path/to/image.png")

        assert result == "image/png"

    def test_detect_content_type_unknown(self, uds_client):
        """Test content type detection for unknown extension."""
        result = uds_client.images._detect_content_type(
            "/path/to/file.unknown"
        )

        assert result == "image/jpeg"

    async def test_upload_from_bytes_requires_content_type(self, uds_client):
        """Test that upload from bytes requires content_type."""
        with pytest.raises(UDSImageUnsupportedSourceError) as exc_info:
            await uds_client.images.upload(b"image data")

        assert "content_type is required" in str(exc_info.value)

    async def test_upload_from_file_not_found(self, uds_client):
        """Test upload from non-existent file."""
        with pytest.raises(UDSImageReadError) as exc_info:
            await uds_client.images.upload("/nonexistent/file.jpg")

        assert "File not found" in str(exc_info.value)

    async def test_upload_from_file_success(self, uds_client, tmp_path):
        """Test successful upload from file."""
        import aiofiles

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
        """Test successful upload from URL."""
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
        """Test upload failure when downloading from URL."""
        from async_uds_api import UDSImageDownloadError

        respx.get("https://example.com/notfound.jpg").mock(
            return_value=Response(404)
        )

        with pytest.raises(UDSImageDownloadError):
            await uds_client.images.upload("https://example.com/notfound.jpg")

    async def test_upload_from_bytes_success(self, uds_client):
        """Test successful upload from bytes."""
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(200))

        image_bytes = b"fake image data"
        result = await uds_client.images.upload(image_bytes, "image/jpeg")

        assert result == IMAGE_UPLOAD_URL_RESPONSE["imageId"]

    async def test_upload_to_presigned_url_error(self, uds_client):
        """Test error handling when uploading to presigned URL."""
        respx.post("https://api.uds.app/partner/v2/image-upload-url").mock(
            return_value=Response(200, json=IMAGE_UPLOAD_URL_RESPONSE)
        )

        respx.put(
            "https://storage.googleapis.com/test-bucket/test-image"
        ).mock(return_value=Response(500))

        with pytest.raises(UDSImageUploadError):
            await uds_client.images.upload(b"image", "image/jpeg")
