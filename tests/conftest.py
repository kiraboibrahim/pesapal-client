import contextlib
import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import respx
from dotenv import load_dotenv
from httpx import Response

from pesapal_client.v3.client import PesapalClientV3
from pesapal_client.v3.schemas import (
    BillingAddress,
    InitiatePaymentOrderRequest,
    InitiateSubscriptionRequest,
    IPNRegistrationRequest,
    RefundRequest,
    SubscriptionDetails,
)

load_dotenv()


@pytest.fixture(autouse=True)
def mock_auth_request(request):
    """Globally mock the /Auth/RequestToken endpoint for all tests."""
    # Exclude test_auth from using this fixture as it test authentication
    if request.node.name.startswith("test_auth") or request.node.get_closest_marker("live"):
        yield
        return

    with respx.mock(base_url="https://cybqa.pesapal.com/pesapalv3/api") as mock:
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        mock.post("/Auth/RequestToken").mock(
            return_value=Response(200, json={"token": "mocktoken123", "expiryDate": expiry})
        )
        yield


@pytest.fixture
def client_sandbox():
    """PesapalClientV3 sandbox instance"""
    consumer_key = os.getenv("PESAPAL_CONSUMER_KEY", "test_key")
    consumer_secret = os.getenv("PESAPAL_CONSUMER_SECRET", "test_secret")
    client = PesapalClientV3(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        is_sandbox=True,
    )
    with contextlib.closing(client):
        yield client


@pytest.fixture
def sample_billing_address():
    return BillingAddress(
        email_address="test@example.com",
        phone_number="0700123456",
        first_name="John",
        last_name="Doe",
        line_1="123 Main St",
        city="Kampala",
        country_code="UG",
    )


@pytest.fixture
def sample_payment_request(sample_billing_address):
    return InitiatePaymentOrderRequest(
        id=str(uuid4()),
        currency="UGX",
        amount=1000.0,
        description="Test Payment",
        callback_url="https://example.com/callback",
        notification_id=uuid4(),
        billing_address=sample_billing_address,
    )


@pytest.fixture
def sample_subscription_request(sample_payment_request):
    subscription_details = SubscriptionDetails(start_date="01-09-2025", end_date="01-10-2025", frequency="MONTHLY")
    return InitiateSubscriptionRequest(
        **sample_payment_request.model_dump(), account_number="123456789", subscription_details=subscription_details
    )


@pytest.fixture
def sample_ipn_request():
    return IPNRegistrationRequest(url="https://example.com/ipn/" + str(uuid4()), ipn_notification_type="POST")


@pytest.fixture
def sample_refund_request():
    return RefundRequest(
        confirmation_code="CONF123",
        amount="1000",
        username="test_user",
        remarks="Test refund",
    )


@pytest.fixture(scope="session")
def live_payment_request(client_live):
    import time

    """A payment request that has been initiated in the Pesapal sandbox and has a valid tracking ID."""
    ipn_request_data = IPNRegistrationRequest(
        url="https://webhook.site/" + str(uuid4()),  # disposable webhook URL
        ipn_notification_type="POST",
    )
    time.sleep(5)  # to avoid hitting rate limits
    ipn = client_live.ipn.register_ipn(ipn_request_data=ipn_request_data)

    sample_payment_request = InitiatePaymentOrderRequest(
        id=str(uuid4()),
        currency="UGX",
        amount=1000.0,
        description="Test Payment",
        callback_url="https://example.com/callback",
        notification_id=ipn.ipn_id,
        billing_address=BillingAddress(
            email_address="test@example.com",
            phone_number="0700123456",
            first_name="John",
            last_name="Doe",
            line_1="123 Main St",
            city="Kampala",
            country_code="UG",
        ),
    )
    return sample_payment_request
