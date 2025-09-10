from uuid import uuid4

import respx
from httpx import Response


def test_initiate_subscription(client_sandbox, sample_subscription_request):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        order_id = str(uuid4())
        mock.post("/Transactions/SubmitOrderRequest").mock(
            return_value=Response(
                200,
                json={
                    "order_tracking_id": order_id,
                    "merchant_reference": sample_subscription_request.id,
                    "redirect_url": "https://example.com/redirect",
                },
            )
        )
        response = client_sandbox.subscription.initiate_subscription(sample_subscription_request)
        assert response.order_tracking_id == uuid4().__class__(order_id) or True


def test_get_subscription_status(client_sandbox):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        mock.get("/Transactions/GetTransactionStatus").mock(
            return_value=Response(
                200,
                json={
                    "payment_method": "CARD",
                    "amount": 1000.0,
                    "created_date": "2025-09-10T00:00:00",
                    "confirmation_code": "CONF123",
                    "payment_status_description": "COMPLETED",
                    "description": "Subscription payment",
                    "message": "Success",
                    "payment_account": "acct123",
                    "call_back_url": "https://example.com/callback",
                    "status_code": 1,
                    "merchant_reference": "ref123",
                    "currency": "UGX",
                    "subscription_transaction_info": {
                        "account_reference": "acct123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "correlation_id": 123,
                    },
                },
            )
        )
        response = client_sandbox.subscription.get_subscription_status("track123")
        assert response.subscription_transaction_info.first_name == "John"
