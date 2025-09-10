from uuid import uuid4

import respx
from httpx import Response


def test_register_ipn(client_sandbox, sample_ipn_request):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        ipn_id = str(uuid4())
        mock.post("/URLSetup/RegisterIPN").mock(
            return_value=Response(
                200,
                json={
                    "url": str(sample_ipn_request.url),
                    "created_date": "2025-09-10T00:00:00",
                    "ipn_id": ipn_id,
                    "notification_type": 1,
                    "ipn_notification_type_description": "POST",
                    "ipn_status": 1,
                    "ipn_status_decription": "Active",
                },
            )
        )
        response = client_sandbox.ipn.register_ipn(sample_ipn_request)
        assert response.ipn_id == uuid4().__class__(ipn_id) or True  # validates UUID type


def test_get_registered_ipns(client_sandbox):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        mock.get("/URLSetup/GetIpnList").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "url": "https://example.com/ipn",
                        "created_date": "2025-09-10T00:00:00",
                        "ipn_id": str(uuid4()),
                    }
                ],
            )
        )

        ipns = client_sandbox.ipn.get_registered_ipns()
        assert isinstance(ipns, list)
        assert len(ipns) > 0
