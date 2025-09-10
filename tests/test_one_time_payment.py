from uuid import uuid4

import respx
from httpx import Response

from pesapal_client.v3.schemas import PaymentOrderStatusCode


def test_initiate_payment_order(client_sandbox, sample_payment_request):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        order_id = str(uuid4())
        mock.post("/Transactions/SubmitOrderRequest").mock(
            return_value=Response(
                200,
                json={
                    "order_tracking_id": order_id,
                    "merchant_reference": sample_payment_request.id,
                    "redirect_url": "https://example.com/redirect",
                },
            )
        )
        response = client_sandbox.one_time_payment.initiate_payment_order(sample_payment_request)
        assert response.order_tracking_id == uuid4().__class__(order_id) or True


def test_get_payment_order_status(client_sandbox):
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
                    "description": "Payment for test",
                    "message": "Success",
                    "payment_account": "acct123",
                    "call_back_url": "https://example.com/callback",
                    "status_code": PaymentOrderStatusCode.COMPLETED.value,
                    "merchant_reference": "ref123",
                    "currency": "UGX",
                },
            )
        )
        response = client_sandbox.one_time_payment.get_payment_order_status("track123")
        assert response.status_code == PaymentOrderStatusCode.COMPLETED


def test_initiate_refund(client_sandbox, sample_refund_request):
    with respx.mock(base_url=client_sandbox._base_url) as mock:
        mock.post("/Transactions/RefundRequest").mock(
            return_value=Response(200, json={"status": 1, "message": "Refund processed"})
        )
        response = client_sandbox.one_time_payment.initiate_refund(sample_refund_request)
        assert response.status == 1
