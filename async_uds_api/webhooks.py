import hashlib
import hmac


def verify_webhook_signature(
    request_id: str,
    timestamp: str,
    company_id: str,
    api_key: str,
    signature: str,
) -> bool:
    """
    Verify webhook X-Signature header.

    Signature = md5(concat(X-RequestId, X-Timestamp, Client-Id, Api-Key))

    Args:
        request_id: X-RequestId header value
        timestamp: X-Timestamp header value
        company_id: Company ID (Client-Id)
        api_key: API key
        signature: X-Signature header value to verify

    Returns:
        True if signature is valid, False otherwise
    """
    concatenated = f"{request_id}{timestamp}{company_id}{api_key}"
    expected_signature = hashlib.md5(concatenated.encode()).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
