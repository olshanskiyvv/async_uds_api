import hashlib

from async_uds_api import UDSClient


class TestWebhooks:
    def test_verify_webhook_signature_valid(self):
        """Test valid webhook signature from OpenAPI example."""
        client = UDSClient(
            company_id="123456",
            api_key="ZWY5ZmI4ZjQtNTgxMC00M2M3LWE2YTYtZGVhMDRmZTAwNzQxCg==",
        )
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = client.verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            signature=signature,
        )

        assert result is True

    def test_verify_webhook_signature_invalid(self):
        """Test invalid webhook signature."""
        client = UDSClient(company_id="123456", api_key="test-api-key")

        result = client.verify_webhook_signature(
            request_id="test-request-id",
            timestamp="2024-01-01T12:00:00Z",
            signature="invalid-signature",
        )

        assert result is False

    def test_verify_webhook_signature_wrong_api_key(self):
        """Test webhook signature with wrong API key."""
        client = UDSClient(company_id="123456", api_key="wrong-api-key")
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = client.verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            signature=signature,
        )

        assert result is False

    def test_verify_webhook_signature_wrong_company_id(self):
        """Test webhook signature with wrong company ID."""
        client = UDSClient(
            company_id="999999",
            api_key="ZWY5ZmI4ZjQtNTgxMC00M2M3LWE2YTYtZGVhMDRmZTAwNzQxCg==",
        )
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        signature = "dc8d4416d3e01a40fd10f1c7bf3f4754"

        result = client.verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            signature=signature,
        )

        assert result is False

    def test_verify_webhook_signature_md5_format(self):
        """Test that signature is MD5 hex format."""
        client = UDSClient(company_id="123", api_key="test-key")
        request_id = "test-id"
        timestamp = "2024-01-01T00:00:00Z"

        concatenated = f"{request_id}{timestamp}123test-key"
        expected = hashlib.md5(concatenated.encode()).hexdigest()

        result = client.verify_webhook_signature(
            request_id=request_id,
            timestamp=timestamp,
            signature=expected,
        )

        assert result is True
        assert len(expected) == 32
