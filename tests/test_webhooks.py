
from async_uds_api import verify_webhook_signature


class TestWebhooks:
    def test_verify_webhook_signature_valid(self):
        """Test valid webhook signature from OpenAPI example."""
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        company_id = 123456
        api_key = "ZWY5ZmI4ZjQtNTgxMC00M2M3LWE2YTYtZGVhMDRmZTAwNzQxCg=="
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            company_id=company_id,
            api_key=api_key,
            signature=signature,
        )

        assert result is True

    def test_verify_webhook_signature_invalid(self):
        """Test invalid webhook signature."""
        result = verify_webhook_signature(
            request_id="test-request-id",
            timestamp="2024-01-01T12:00:00Z",
            company_id=123456,
            api_key="test-api-key",
            signature="invalid-signature",
        )

        assert result is False

    def test_verify_webhook_signature_wrong_api_key(self):
        """Test webhook signature with wrong API key."""
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        company_id = 123456
        api_key = "wrong-api-key"
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            company_id=company_id,
            api_key=api_key,
            signature=signature,
        )

        assert result is False

    def test_verify_webhook_signature_wrong_company_id(self):
        """Test webhook signature with wrong company ID."""
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        company_id = 999999
        api_key = "ZWY5ZmI4ZjQtNTgxMC00M2M3LWE2YTYtZGVhMDRmZTAwNzQxCg=="
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            company_id=company_id,
            api_key=api_key,
            signature=signature,
        )

        assert result is False

    def test_verify_webhook_signature_md5_format(self):
        """Test that signature is MD5 hex format."""
        import hashlib

        request_id = "test-id"
        timestamp = "2024-01-01T00:00:00Z"
        company_id = 123
        api_key = "test-key"

        concatenated = f"{request_id}{timestamp}{company_id}{api_key}"
        expected = hashlib.md5(concatenated.encode()).hexdigest()

        result = verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            company_id=company_id,
            api_key=api_key,
            signature=expected,
        )

        assert result is True
        assert len(expected) == 32
