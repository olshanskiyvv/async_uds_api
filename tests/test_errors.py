import pytest

from async_uds_api.errors import (
    UDSAPIError,
    UDSBadRequestError,
    UDSClientError,
    UDSForbiddenError,
    UDSImageDownloadError,
    UDSImageError,
    UDSImageReadError,
    UDSImageSourceError,
    UDSImageUnsupportedSourceError,
    UDSImageUploadError,
    UDSNotFoundError,
    UDSUnauthorizedError,
    UDSUnexpectedError,
)


class TestExceptionHierarchy:
    def test_uds_client_error_is_exception(self):
        """Test UDSClientError inherits from Exception."""
        assert issubclass(UDSClientError, Exception)

    def test_uds_api_error_inherits_from_client_error(self):
        """Test UDSAPIError inherits from UDSClientError."""
        assert issubclass(UDSAPIError, UDSClientError)

    def test_bad_request_error_hierarchy(self):
        """Test UDSBadRequestError hierarchy."""
        assert issubclass(UDSBadRequestError, UDSAPIError)
        assert issubclass(UDSBadRequestError, UDSClientError)

    def test_unauthorized_error_hierarchy(self):
        """Test UDSUnauthorizedError hierarchy."""
        assert issubclass(UDSUnauthorizedError, UDSAPIError)

    def test_forbidden_error_hierarchy(self):
        """Test UDSForbiddenError hierarchy."""
        assert issubclass(UDSForbiddenError, UDSAPIError)

    def test_not_found_error_hierarchy(self):
        """Test UDSNotFoundError hierarchy."""
        assert issubclass(UDSNotFoundError, UDSAPIError)

    def test_unexpected_error_hierarchy(self):
        """Test UDSUnexpectedError hierarchy."""
        assert issubclass(UDSUnexpectedError, UDSAPIError)


class TestImageExceptionHierarchy:
    def test_image_error_hierarchy(self):
        """Test UDSImageError hierarchy."""
        assert issubclass(UDSImageError, UDSClientError)

    def test_image_source_error_hierarchy(self):
        """Test UDSImageSourceError hierarchy."""
        assert issubclass(UDSImageSourceError, UDSImageError)

    def test_image_read_error_hierarchy(self):
        """Test UDSImageReadError hierarchy."""
        assert issubclass(UDSImageReadError, UDSImageSourceError)
        assert issubclass(UDSImageReadError, UDSImageError)
        assert issubclass(UDSImageReadError, UDSClientError)

    def test_image_download_error_hierarchy(self):
        """Test UDSImageDownloadError hierarchy."""
        assert issubclass(UDSImageDownloadError, UDSImageSourceError)
        assert issubclass(UDSImageDownloadError, UDSImageError)

    def test_image_upload_error_hierarchy(self):
        """Test UDSImageUploadError hierarchy."""
        assert issubclass(UDSImageUploadError, UDSImageError)
        assert not issubclass(UDSImageUploadError, UDSImageSourceError)

    def test_image_unsupported_source_error_hierarchy(self):
        """Test UDSImageUnsupportedSourceError hierarchy."""
        assert issubclass(UDSImageUnsupportedSourceError, UDSImageError)
        assert not issubclass(
            UDSImageUnsupportedSourceError, UDSImageSourceError
        )


class TestAPIErrorAttributes:
    def test_uds_api_error_attributes(self):
        """Test UDSAPIError attributes."""
        error = UDSAPIError(
            "Test error",
            status_code=400,
            error_code="TEST_ERROR",
        )

        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"
        assert error.message == "Test error"
        assert str(error) == "400 [errorCode=TEST_ERROR]"

    def test_uds_api_error_without_error_code(self):
        """Test UDSAPIError without error_code."""
        error = UDSAPIError("Test error", status_code=404)

        assert error.status_code == 404
        assert error.error_code is None


class TestExceptionCatching:
    def test_catch_api_error_as_client_error(self):
        """Test catching UDSAPIError as UDSClientError."""
        with pytest.raises(UDSClientError):
            raise UDSAPIError("Test", status_code=400)

    def test_catch_bad_request_as_api_error(self):
        """Test catching UDSBadRequestError as UDSAPIError."""
        with pytest.raises(UDSAPIError):
            raise UDSBadRequestError("Bad request", status_code=400)

    def test_catch_image_read_as_source_error(self):
        """Test catching UDSImageReadError as UDSImageSourceError."""
        with pytest.raises(UDSImageSourceError):
            raise UDSImageReadError("Cannot read file")

    def test_catch_image_read_as_image_error(self):
        """Test catching UDSImageReadError as UDSImageError."""
        with pytest.raises(UDSImageError):
            raise UDSImageReadError("Cannot read file")

    def test_catch_image_read_as_client_error(self):
        """Test catching UDSImageReadError as UDSClientError."""
        with pytest.raises(UDSClientError):
            raise UDSImageReadError("Cannot read file")

    def test_catch_image_download_as_source_error(self):
        """Test catching UDSImageDownloadError as UDSImageSourceError."""
        with pytest.raises(UDSImageSourceError):
            raise UDSImageDownloadError("Cannot download")


class TestExceptionMessages:
    def test_api_error_message(self):
        """Test UDSAPIError keeps server text off str()."""
        error = UDSAPIError(
            "API error",
            status_code=500,
            method="POST",
            path="/operations",
        )
        assert error.message == "API error"
        assert str(error) == "500 for POST /operations"

    def test_image_error_message(self):
        """Test UDSImageError message."""
        error = UDSImageError("Image error")
        assert str(error) == "Image error"

    def test_image_read_error_message(self):
        """Test UDSImageReadError message."""
        error = UDSImageReadError("File not found: test.jpg")
        assert "File not found" in str(error)
