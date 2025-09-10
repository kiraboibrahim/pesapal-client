import os
from uuid import uuid4

import pytest
from dotenv import load_dotenv

from pesapal_client import PesapalClientV3
from pesapal_client.utils import is_jwt_expired
from pesapal_client.v3.schemas import (
    IPNRegistrationRequest,
    RefundRequest,
)

load_dotenv()


@pytest.fixture(scope="session")
def client_live():
    key = os.getenv("PESAPAL_CONSUMER_KEY")
    secret = os.getenv("PESAPAL_CONSUMER_SECRET")
    if not key or not secret:
        pytest.skip("Sandbox credentials not set")
    return PesapalClientV3(
        consumer_key=key,
        consumer_secret=secret,
        is_sandbox=True,
    )


@pytest.mark.live
def test_auth_live(client_live):
    token = client_live.auth.get_auth_token()
    assert token
    assert not is_jwt_expired(token)


@pytest.mark.live
def test_register_ipn_live(client_live):
    ipn_data = IPNRegistrationRequest(
        url="https://webhook.site/" + str(uuid4()),
        ipn_notification_type="POST",
    )
    resp = client_live.ipn.register_ipn(ipn_data)
    assert resp.url == str(ipn_data.url)
    assert resp.ipn_status in (0, 1)


@pytest.mark.live
def test_get_ipns_live(client_live):
    ipns = client_live.ipn.get_registered_ipns()
    assert isinstance(ipns, list)


@pytest.mark.live
def test_initiate_payment_live(client_live, live_payment_request):
    resp = client_live.one_time_payment.initiate_payment_order(live_payment_request)
    assert resp.redirect_url
    assert resp.order_tracking_id


@pytest.mark.skip(reason="Requires a completed transaction ID to test against")
def test_get_payment_status_live(client_live, live_payment_request):
    """
    I have failed to find a way to reliably test this without having a valid completed transaction ID.
    Trying to initiate a payment and immediately check its status returns an "INVALID" status which is considered
    as an error, since the user has to redirected to the pesapal page to complete the payment.
    """
    payment_request = client_live.one_time_payment.initiate_payment_order(live_payment_request)
    status = client_live.one_time_payment.get_payment_order_status(payment_request.order_tracking_id)
    assert status.status_code


@pytest.mark.skip(reason="Requires a completed transaction ID to test against")
def test_refund_live(client_live, live_payment_request):
    """
    I have failed to find a way to reliably test this without having a valid completed transaction ID.
    It is the same case as with test_get_payment_status_live above.
    """
    refund = RefundRequest(
        confirmation_code="0987775444",
        amount="1000",
        username="sandbox_user",
        remarks="Testing refund",
    )
    resp = client_live.one_time_payment.initiate_refund(refund)
    assert resp.status in (0, 1)
