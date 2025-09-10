import os
from datetime import datetime, timedelta

import respx
from dotenv import load_dotenv
from httpx import Response

load_dotenv()


def test_auth_token_fetch(client_sandbox):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        sample_token = os.getenv("PESAPAL_MOCK_TOKEN", "not-a-real-token")
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        mock.post("/Auth/RequestToken").mock(
            return_value=Response(200, json={"token": sample_token, "expiryDate": expiry})
        )
        auth_token = client_sandbox._get_auth_token()
        assert auth_token


def test_auth_token_header_added(client_sandbox):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        sample_token = os.getenv("PESAPAL_MOCK_TOKEN", "not-a-real-token")
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        mock.post("/Auth/RequestToken").mock(
            return_value=Response(200, json={"token": sample_token, "expiryDate": expiry})
        )
        # Trigger a fake request to invoke _ensure_valid_auth_token
        request = client_sandbox._client.build_request("GET", "/Transactions/GetTransactionStatus")
        client_sandbox._ensure_valid_auth_token(request)
        assert request.headers.get("Authorization") == f"Bearer {sample_token}"
